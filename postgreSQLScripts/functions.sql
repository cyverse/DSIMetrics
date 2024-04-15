CREATE OR REPLACE FUNCTION hashRegistree(text) returns bigint as $$
 select ('x'||substr(md5($1),1,16))::bit(64)::bigint;
$$ language sql;

DROP FUNCTION createSeriesNotification() CASCADE;

CREATE FUNCTION createSeriesNotification() RETURNS TRIGGER AS $$
BEGIN
    EXECUTE 'NOTIFY newSeries, ''' || row_to_json(NEW)::text || '''';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER series_insert_trigger
AFTER INSERT ON series
FOR EACH ROW
EXECUTE FUNCTION createSeriesNotification();

