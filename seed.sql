INSERT INTO users (`email`, `name`, `api_key`) VALUES ('admin@admin.com', 'admin', 'abc123');

INSERT INTO notes (`note_content`) VALUES ('{"header":"Context to my nugget","body":"My super golden nugget punchline","footer":"Some extra thoughts about it"}');

INSERT INTO notes_users (`id_note`, `id_user`) VALUES (1, 1);