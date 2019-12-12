/*CREATE USER IF NOT EXISTS 'hackernews'@'%' IDENTIFIED BY 'hackernews';
CREATE DATABASE hackernews;
GRANT ALL PRIVILEGES ON hackernews.* TO 'hackernews'@'%';
FLUSH PRIVILEGES;
*/
USE hackernews;

DROP TABLE IF EXISTS comment_vote;
DROP TABLE IF EXISTS post_vote;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(64) NOT NULL UNIQUE,
	password VARCHAR(256) NOT NULL,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	email VARCHAR(256) UNIQUE,
	karma INTEGER DEFAULT 0,
	about VARCHAR(512)
);

CREATE TABLE post (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(64) NOT NULL UNIQUE,
	url VARCHAR(512),
	body VARCHAR(512),
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	edited BIT DEFAULT 0,
	votes INTEGER DEFAULT 0,
	user_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE comment (
	id INTEGER AUTO_INCREMENT PRIMARY KEY,
	body VARCHAR(512),
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	votes INTEGER DEFAULT 0,
	edited BIT DEFAULT 0,
	parent_id INTEGER DEFAULT NULL, 
	user_id INTEGER NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (parent_id) REFERENCES comment (id)
);

CREATE TABLE post_vote (
	user_id INTEGER,
	post_id INTEGER,
	positive BIT DEFAULT 0,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id, post_id),
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (post_id) REFERENCES post (id)
);

CREATE TABLE comment_vote (
	user_id INTEGER,
	comment_id INTEGER,
	positive BIT DEFAULT 0,
	created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (user_id, comment_id),
	FOREIGN KEY (user_id) REFERENCES user (id),
	FOREIGN KEY (comment_id) REFERENCES comment (id)
);
