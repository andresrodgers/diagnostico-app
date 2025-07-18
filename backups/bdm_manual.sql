-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: base_datos_maestra
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `characteristic_value_mappings`
--

DROP TABLE IF EXISTS `characteristic_value_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `characteristic_value_mappings` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `characteristic_id` bigint NOT NULL,
  `value_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `characteristic_id` (`characteristic_id`,`value_id`),
  KEY `idx_cvm_char` (`characteristic_id`),
  KEY `idx_cvm_value` (`value_id`),
  CONSTRAINT `characteristic_value_mappings_ibfk_1` FOREIGN KEY (`characteristic_id`) REFERENCES `characteristics` (`id`),
  CONSTRAINT `characteristic_value_mappings_ibfk_2` FOREIGN KEY (`value_id`) REFERENCES `characteristic_values` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `characteristic_value_mappings`
--

LOCK TABLES `characteristic_value_mappings` WRITE;
/*!40000 ALTER TABLE `characteristic_value_mappings` DISABLE KEYS */;
/*!40000 ALTER TABLE `characteristic_value_mappings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `characteristic_values`
--

DROP TABLE IF EXISTS `characteristic_values`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `characteristic_values` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `characteristic_id` bigint NOT NULL,
  `value` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `characteristic_id` (`characteristic_id`,`value`),
  KEY `idx_charvals_charid` (`characteristic_id`),
  CONSTRAINT `characteristic_values_ibfk_1` FOREIGN KEY (`characteristic_id`) REFERENCES `characteristics` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `characteristic_values`
--

LOCK TABLES `characteristic_values` WRITE;
/*!40000 ALTER TABLE `characteristic_values` DISABLE KEYS */;
/*!40000 ALTER TABLE `characteristic_values` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `characteristics`
--

DROP TABLE IF EXISTS `characteristics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `characteristics` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `unspsc_code_id` bigint NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hierarchy_level` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unspsc_code_id` (`unspsc_code_id`,`name`),
  KEY `idx_char_unspsc` (`unspsc_code_id`),
  CONSTRAINT `characteristics_ibfk_1` FOREIGN KEY (`unspsc_code_id`) REFERENCES `unspsc_codes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `characteristics`
--

LOCK TABLES `characteristics` WRITE;
/*!40000 ALTER TABLE `characteristics` DISABLE KEYS */;
/*!40000 ALTER TABLE `characteristics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `code_mappings`
--

DROP TABLE IF EXISTS `code_mappings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `code_mappings` (
  `code_v14` bigint NOT NULL,
  `unspsc_code_id` bigint NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `source` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`code_v14`),
  KEY `unspsc_code_id` (`unspsc_code_id`),
  CONSTRAINT `code_mappings_ibfk_1` FOREIGN KEY (`unspsc_code_id`) REFERENCES `unspsc_codes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `code_mappings`
--

LOCK TABLES `code_mappings` WRITE;
/*!40000 ALTER TABLE `code_mappings` DISABLE KEYS */;
/*!40000 ALTER TABLE `code_mappings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diagnostic_history`
--

DROP TABLE IF EXISTS `diagnostic_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnostic_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `catalog_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `analysis_date` timestamp NOT NULL,
  `total_rows` bigint NOT NULL,
  `total_duplicates` bigint NOT NULL,
  `new_materials` bigint NOT NULL,
  `updated_materials` bigint NOT NULL,
  `total_time` time NOT NULL,
  `status` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_diag_analysis_date` (`analysis_date`),
  KEY `idx_diag_status` (`status`),
  KEY `idx_diag_new_materials` (`new_materials`),
  KEY `idx_diag_catalog_name` (`catalog_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnostic_history`
--

LOCK TABLES `diagnostic_history` WRITE;
/*!40000 ALTER TABLE `diagnostic_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `diagnostic_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material_characteristics`
--

DROP TABLE IF EXISTS `material_characteristics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `material_characteristics` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_id` bigint NOT NULL,
  `cvm_id` bigint NOT NULL,
  `display_order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `material_id` (`material_id`,`cvm_id`),
  KEY `idx_mc_material` (`material_id`),
  KEY `idx_mc_cvm` (`cvm_id`),
  CONSTRAINT `material_characteristics_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `validated_materials` (`id`) ON DELETE CASCADE,
  CONSTRAINT `material_characteristics_ibfk_2` FOREIGN KEY (`cvm_id`) REFERENCES `characteristic_value_mappings` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material_characteristics`
--

LOCK TABLES `material_characteristics` WRITE;
/*!40000 ALTER TABLE `material_characteristics` DISABLE KEYS */;
/*!40000 ALTER TABLE `material_characteristics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unspsc_codes`
--

DROP TABLE IF EXISTS `unspsc_codes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unspsc_codes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code_v26` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `code_v14` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `product_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_v26` (`code_v26`),
  UNIQUE KEY `code_v14` (`code_v14`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unspsc_codes`
--

LOCK TABLES `unspsc_codes` WRITE;
/*!40000 ALTER TABLE `unspsc_codes` DISABLE KEYS */;
/*!40000 ALTER TABLE `unspsc_codes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `update_history`
--

DROP TABLE IF EXISTS `update_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `update_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `column_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_value` text COLLATE utf8mb4_unicode_ci,
  `new_value` text COLLATE utf8mb4_unicode_ci,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_update_tbl_col` (`table_name`,`column_name`),
  KEY `idx_update_date` (`updated_at`),
  KEY `idx_update_tbl_date` (`table_name`,`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `update_history`
--

LOCK TABLES `update_history` WRITE;
/*!40000 ALTER TABLE `update_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `update_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_long_description`
--

DROP TABLE IF EXISTS `v_long_description`;
/*!50001 DROP VIEW IF EXISTS `v_long_description`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_long_description` AS SELECT 
 1 AS `material_id`,
 1 AS `long_description`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `validated_materials`
--

DROP TABLE IF EXISTS `validated_materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `validated_materials` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `unspsc_code_id` bigint NOT NULL,
  `description_hash` char(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `description_hash` (`description_hash`),
  KEY `idx_valid_mat_unspsc` (`unspsc_code_id`),
  CONSTRAINT `validated_materials_ibfk_1` FOREIGN KEY (`unspsc_code_id`) REFERENCES `unspsc_codes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `validated_materials`
--

LOCK TABLES `validated_materials` WRITE;
/*!40000 ALTER TABLE `validated_materials` DISABLE KEYS */;
/*!40000 ALTER TABLE `validated_materials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'base_datos_maestra'
--

--
-- Final view structure for view `v_long_description`
--

/*!50001 DROP VIEW IF EXISTS `v_long_description`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_long_description` AS select `vm`.`id` AS `material_id`,concat_ws('; ',`uc`.`product_name`,group_concat(concat(`c`.`name`,':',`cv`.`value`) order by `mc`.`display_order` ASC separator '; ')) AS `long_description` from (((((`validated_materials` `vm` join `unspsc_codes` `uc` on((`uc`.`id` = `vm`.`unspsc_code_id`))) join `material_characteristics` `mc` on((`mc`.`material_id` = `vm`.`id`))) join `characteristic_value_mappings` `cvm` on((`cvm`.`id` = `mc`.`cvm_id`))) join `characteristics` `c` on((`c`.`id` = `cvm`.`characteristic_id`))) join `characteristic_values` `cv` on((`cv`.`id` = `cvm`.`value_id`))) group by `vm`.`id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-09 15:53:12
