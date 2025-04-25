attendance-system/
├── common/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── company.py
│   │   └── subscription.py
│   ├── db.py
│   └── enums.py
├── services/
│   ├── auth/
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── users/
│   ├── companies/
│   ├── subscriptions/
│   └── attendance/
├── main.py
├── docker-compose.yml         # Configuración para orquestar todos los servicios
└── README.md                  # Documentación del proyecto
