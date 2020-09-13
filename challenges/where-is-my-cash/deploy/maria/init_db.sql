--- Create securecash user
CREATE USER IF NOT EXISTS 'securecash'@'%';
GRANT USAGE ON *.* TO 'securecash'@'%';
GRANT SELECT,INSERT ON *.* TO 'securecash'@'%';

--- Create database
CREATE DATABASE IF NOT EXISTS `securecash`;
CREATE TABLE IF NOT EXISTS `securecash`.`general` (
	user_id CHAR(36) PRIMARY KEY,
	username VARCHAR(50) NOT NULL,
	password CHAR(64),
	api_key CHAR(30),
	admin BOOLEAN DEFAULT 0,
	UNIQUE (api_key));
CREATE TABLE IF NOT EXISTS `securecash`.`wallets` (
	wallet_id CHAR(20) PRIMARY KEY,
	owner_id CHAR(36),
	balance DECIMAL(13,2) NOT NULL,
	note VARCHAR(255));

--- Inser initial data
INSERT IGNORE INTO `securecash`.`general` VALUES
	('13371337-1337-1337-1337-133713371335', 'local_it_staff',
	 '__IT_PASSWORD__',
	 '__IT_API_KEY__', true),
	('13371337-1337-1337-1337-133713371336', 'h4ppy_f33t',
	 '__ADMIN_PASSWORD__',
	 '__ADMIN_API_KEY__', true),
	('13371337-1337-1337-1337-133713371337', 'bob_h4x0r',
	 '__FRIEND_PASSWORD__',
	 '__FRIEND_API_KEY__', false);
INSERT IGNORE INTO `securecash`.`wallets` VALUES
	('13371337133713371337', '13371337-1337-1337-1337-133713371337',
	 '1337.00', '__FLAG__');
