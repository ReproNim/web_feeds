CREATE TABLE config (name TEXT PRIMARY KEY, 
                     value TEXT);

CREATE TABLE event (id SERIAL PRIMARY KEY, 
                    active BOOLEAN NOT NULL DEFAULT TRUE, 
                    time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), 
                    source TEXT NOT NULL CHECK (source IN ('email', 
                                                           'hypothesis')), 
                    source_user TEXT NOT NULL, 
                    source_id TEXT DEFAULT NULL, 
                    url TEXT NOT NULL, 
                    headline TEXT NOT NULL);

-- eof
