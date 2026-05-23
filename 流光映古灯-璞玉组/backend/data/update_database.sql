-- 添加工艺特点和历史背景字段到古代精品灯具表
ALTER TABLE `古代精品灯具` ADD COLUMN `工艺特点` TEXT DEFAULT NULL;
ALTER TABLE `古代精品灯具` ADD COLUMN `历史背景` TEXT DEFAULT NULL;
