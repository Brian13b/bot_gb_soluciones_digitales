import os
from getpass import getpass
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.models import User
from admin.core.security import hash_password
import sys
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # Obtener DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ Error: DATABASE_URL no configurada en variables de entorno")
        print("   Configura .env con tu URL de PostgreSQL")
        sys.exit(1)
    
    # Conectar a BD
    try:
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        
        # Obtener datos del usuario
        print("\n📝 Crear usuario administrador\n")
        
        email = input("Email: ").strip()
        if not email or "@" not in email:
            print("❌ Email inválido")
            sys.exit(1)
        
        password = getpass("Contraseña: ")
        password_confirm = getpass("Confirmar contraseña: ")
        
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden")
            sys.exit(1)
        
        if len(password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            sys.exit(1)
        
        # Crear usuario
        db = SessionLocal()
        
        # Verificar si el usuario ya existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"❌ El usuario {email} ya existe")
            db.close()
            sys.exit(1)
        
        # Crear nuevo usuario
        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            password_hash=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"\n✅ Usuario creado exitosamente!")
        print(f"   Email: {email}")
        print(f"   ID: {new_user.id}")
        print(f"\n   Puedes ingresar al panel con estas credenciales")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()