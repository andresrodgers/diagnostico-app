
USE base_datos_maestra;

-- 1) CÓDIGOS UNSPSC + nombre base
CREATE TABLE IF NOT EXISTS unspsc_codes (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,            -- PK interna
  code_v26   VARCHAR(16) NOT NULL UNIQUE,                  -- Código v2.6
  code_v14   VARCHAR(16) UNIQUE,                           -- Código v1.4 (puede ser NULL)
  product_name VARCHAR(255) NOT NULL                       --  Nombre genérico del producto
);

CREATE TABLE IF NOT EXISTS code_mappings (
  code_v14        BIGINT PRIMARY KEY,          -- código viejo
  unspsc_code_id  BIGINT NOT NULL,             -- apunta al código nuevo
  created_at      TIMESTAMP NOT NULL           -- ← NUEVO: cuándo se creó
                   DEFAULT CURRENT_TIMESTAMP,
  source          VARCHAR(100),                -- ← NUEVO: quién/qué lo creó
  FOREIGN KEY (unspsc_code_id) REFERENCES unspsc_codes(id)
);

-- 2) CARACTERÍSTICAS POR CÓDIGO  
CREATE TABLE IF NOT EXISTS characteristics (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  unspsc_code_id   BIGINT NOT NULL,
  name             VARCHAR(100) NOT NULL,
  hierarchy_level  INT NOT NULL,
  UNIQUE (unspsc_code_id, name),
  FOREIGN KEY (unspsc_code_id) REFERENCES unspsc_codes(id)
);
CREATE INDEX idx_char_unspsc ON characteristics(unspsc_code_id);

 -- 3) VALORES POR CARACTERÍSTICA
CREATE TABLE IF NOT EXISTS characteristic_values (
  id                BIGINT PRIMARY KEY AUTO_INCREMENT,
  characteristic_id BIGINT NOT NULL,
  value             VARCHAR(255) NOT NULL,
  UNIQUE (characteristic_id, value),
  FOREIGN KEY (characteristic_id) REFERENCES characteristics(id)
);
CREATE INDEX idx_charvals_charid ON characteristic_values(characteristic_id);

-- 4) CATÁLOGO PARES CARACTERÍSTICA-VALOR
CREATE TABLE IF NOT EXISTS characteristic_value_mappings (
  id                BIGINT PRIMARY KEY AUTO_INCREMENT,
  characteristic_id BIGINT NOT NULL,
  value_id          BIGINT NOT NULL,
  UNIQUE (characteristic_id, value_id),
  FOREIGN KEY (characteristic_id) REFERENCES characteristics(id),
  FOREIGN KEY (value_id)         REFERENCES characteristic_values(id)
);
CREATE INDEX idx_cvm_char  ON characteristic_value_mappings(characteristic_id);
CREATE INDEX idx_cvm_value ON characteristic_value_mappings(value_id);

-- 5) MATERIALES VALIDOS
CREATE TABLE IF NOT EXISTS validated_materials (
  id               BIGINT PRIMARY KEY AUTO_INCREMENT,
  unspsc_code_id   BIGINT NOT NULL,
  description_hash CHAR(64) UNIQUE,                        -- SHA-256 de la lista CVM
  FOREIGN KEY (unspsc_code_id) REFERENCES unspsc_codes(id)
);
CREATE INDEX idx_valid_mat_unspsc ON validated_materials(unspsc_code_id);

-- 6) CARACTERÍSTICAS ASIGNADAS A CADA MATERIAL
CREATE TABLE IF NOT EXISTS material_characteristics (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  material_id   BIGINT NOT NULL,
  cvm_id        BIGINT NOT NULL,
  display_order INT,
  UNIQUE (material_id, cvm_id),
  FOREIGN KEY (material_id) REFERENCES validated_materials(id) ON DELETE CASCADE,
  FOREIGN KEY (cvm_id)      REFERENCES characteristic_value_mappings(id) ON DELETE RESTRICT
);
CREATE INDEX idx_mc_material ON material_characteristics(material_id);
CREATE INDEX idx_mc_cvm      ON material_characteristics(cvm_id);

-- 7) AUDITORÍA DE CAMBIOS
CREATE TABLE IF NOT EXISTS update_history (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  table_name  VARCHAR(100) NOT NULL,
  column_name VARCHAR(100) NOT NULL,
  old_value   TEXT,
  new_value   TEXT,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_update_tbl_col ON update_history(table_name,column_name);
CREATE INDEX idx_update_date    ON update_history(updated_at);
CREATE INDEX idx_update_tbl_date ON update_history(table_name, updated_at);

-- 8) HISTORIAL DE EJECUCIONES DEL DIAGNÓSTICO
CREATE TABLE IF NOT EXISTS diagnostic_history (
  id                BIGINT PRIMARY KEY AUTO_INCREMENT,
  catalog_name      VARCHAR(255) NOT NULL,
  analysis_date     TIMESTAMP    NOT NULL,
  total_rows        BIGINT       NOT NULL,
  total_duplicates  BIGINT       NOT NULL,
  new_materials     BIGINT       NOT NULL,
  updated_materials BIGINT       NOT NULL,
  total_time        TIME         NOT NULL,
  status            VARCHAR(50)  NOT NULL,
  notes             TEXT
);
CREATE INDEX idx_diag_analysis_date  ON diagnostic_history(analysis_date);
CREATE INDEX idx_diag_status         ON diagnostic_history(status);
CREATE INDEX idx_diag_new_materials  ON diagnostic_history(new_materials);
CREATE INDEX idx_diag_catalog_name ON diagnostic_history(catalog_name);



