set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Validate database structure
    DO \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'news_articles'
        ) THEN
            RAISE EXCEPTION 'Table news_articles does not exist';
        END IF;
    END
    \$\$;
EOSQL
