-- Crear tabla employees para Dashboard Gestión Carnicería
-- Creado por Ezio Camporeale

CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    address TEXT,
    position VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    hire_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Activo',
    contract_type VARCHAR(100) DEFAULT 'Tiempo Completo',
    emergency_contact TEXT,
    emergency_phone VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_employees_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION update_employees_updated_at();

-- Insertar algunos empleados de ejemplo (opcional)
INSERT INTO employees (name, email, phone, position, department, salary, hire_date, status) VALUES
('Orlando Garcia', 'orlando.garcia@carniceria.com', '+54 11 1234-5678', 'Carnicero Principal', 'Producción', 1830.00, '2024-11-22', 'Activo')
ON CONFLICT (email) DO NOTHING;

-- Verificar que la tabla se creó correctamente
SELECT 'Tabla employees creada exitosamente' as status;
SELECT COUNT(*) as total_employees FROM employees;
