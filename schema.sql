DROP TABLE IF EXISTS tocados;
DROP TABLE IF EXISTS correos;
DROP TABLE IF EXISTS ataques;
DROP TABLE IF EXISTS personas;

CREATE TABLE personas (
    id INTEGER,
    nombre TEXT,
    PRIMARY KEY (id)
);
CREATE TABLE correos (
    id TEXT,
    persona INTEGER,
    avisado INTEGER not null default 0,
    PRIMARY KEY (id)
    FOREIGN KEY(persona) REFERENCES personas(id)
);
CREATE TABLE ataques (
    id TEXT,
    titulo TEXT,
    dominio TEXT,
    descripcion TEXT,
    info TEXT,
    PRIMARY KEY (id)
);
CREATE TABLE tocados (
    correo TEXT,
    ataque TEXT,
    FOREIGN KEY(correo) REFERENCES correos(id),
    FOREIGN KEY(ataque) REFERENCES ataques(id)
);

