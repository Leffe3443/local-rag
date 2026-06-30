CREATE OR REPLACE FUNCTION match_events(
    query_embedding vector(768),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id        bigint,
    title     varchar,
    date      timestamptz,
    summary   varchar,
    url       varchar,
    type      varchar,
    lat       float,
    lon       float,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        e.id, e.title, e.date, e.summary, e.url, e.type, e.lat, e.lon,
        1 - (e.embedding <=> query_embedding) AS similarity
    FROM events_db e
    WHERE e.embedding IS NOT NULL
      AND 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding   -- closest first
    LIMIT match_count;
$$;