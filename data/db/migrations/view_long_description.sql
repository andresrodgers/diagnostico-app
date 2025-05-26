 -- 9) VISTA PARA RECONSTRUIR LA DESCRIPCIÓN LARGA 
CREATE OR REPLACE VIEW v_long_description AS
SELECT
  vm.id                                                  AS material_id,
  CONCAT_WS('; ',
    uc.product_name,
    GROUP_CONCAT(CONCAT(c.name, ':', cv.value)
                 ORDER BY mc.display_order SEPARATOR '; ')
  )                                                     AS long_description
FROM validated_materials          vm
JOIN unspsc_codes                 uc ON uc.id = vm.unspsc_code_id
JOIN material_characteristics     mc ON mc.material_id = vm.id
JOIN characteristic_value_mappings cvm ON cvm.id = mc.cvm_id
JOIN characteristics              c ON c.id  = cvm.characteristic_id
JOIN characteristic_values        cv ON cv.id = cvm.value_id
GROUP BY vm.id;