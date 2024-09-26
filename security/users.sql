CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(45) NOT NULL,
  `password` varchar(60) NOT NULL,
  `user_group` varchar(45) NOT NULL,
  `refresh_token` text,
  `is_active` tinyint DEFAULT '0',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `login_UNIQUE` (`email`)
)