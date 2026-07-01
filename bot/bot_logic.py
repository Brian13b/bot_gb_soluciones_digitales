import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI
from bot.services.servicio_manager import ServicioManager

load_dotenv()

class BotLogic:
    def __init__(self):
        self.manager = ServicioManager()
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.startswith("sk-"):
            self.client = OpenAI(api_key=api_key)
            print("✅ Conexión con OpenAI establecida.")
        else:
            self.client = None

    def _cargar_system_prompt(self):
        """Lee el System Prompt directamente desde el archivo Markdown."""
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_prompt = os.path.join(ruta_actual, "SYSTEM_PROMPT.md")
        try:
            with open(ruta_prompt, "r", encoding="utf-8") as archivo:
                return archivo.read()
        except Exception as e:
            print(f"❌ Error cargando System Prompt: {e}")
            return "Eres el asistente de GB Soluciones Digitales."

    def _parse_extraction_json(self, text: str) -> dict:
        """Extrae JSON entre [CONTACT_EXTRACTION] y [/CONTACT_EXTRACTION]"""
        match = re.search(r'\[CONTACT_EXTRACTION\](.*?)\[/CONTACT_EXTRACTION\]', text, re.DOTALL)
        if match:
            try:
                extraction_str = match.group(1).strip()
                return json.loads(extraction_str)
            except (json.JSONDecodeError, ValueError):
                return {
                    "name": None,
                    "email": None,
                    "phone": None,
                    "extraction_confidence": 0.0,
                    "extraction_method": "none"
                }
        return {
            "name": None,
            "email": None,
            "phone": None,
            "extraction_confidence": 0.0,
            "extraction_method": "none"
        }

    def _strip_extraction_markers(self, text: str) -> str:
        """Quita los markers de extracción para respuesta visible"""
        return re.sub(
            r'\[CONTACT_EXTRACTION\].*?\[/CONTACT_EXTRACTION\]',
            '',
            text,
            flags=re.DOTALL
        ).strip()

    def procesar(self, mensaje, history=[], channel="web"):
        if not self.client:
            return {
                "respuesta": "Modo offline activado.",
                "extracted_contact": {
                    "name": None,
                    "email": None,
                    "phone": None,
                    "extraction_confidence": 0.0,
                    "extraction_method": "none"
                }
            }

        catalogo = self.manager.obtener_catalogo_completo()
        system_prompt_base = self._cargar_system_prompt()

        system_prompt = system_prompt_base.replace("{catalogo}", catalogo)
        system_prompt += f"\n\nCONTEXTO DE CANAL: El usuario se comunica a través de {channel}."

        mensajes_api = [{"role": "system", "content": system_prompt}]
        mensajes_api.extend(history)
        mensajes_api.append({"role": "user", "content": mensaje})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=mensajes_api,
                temperature=0.3,
                max_tokens=300
            )
            respuesta_completa = response.choices[0].message.content

            # Extraer JSON y limpiar respuesta visible
            extracted_contact = self._parse_extraction_json(respuesta_completa)
            visible_response = self._strip_extraction_markers(respuesta_completa)

            return {
                "respuesta": visible_response,
                "extracted_contact": extracted_contact
            }
        except Exception as e:
            print(f"Error de conexión con OpenAI: {e}")
            return {
                "respuesta": "Hubo un error al procesar tu consulta.",
                "extracted_contact": {
                    "name": None,
                    "email": None,
                    "phone": None,
                    "extraction_confidence": 0.0,
                    "extraction_method": "none"
                }
            }