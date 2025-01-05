CREATE TABLE public.film (
    film_id integer NOT NULL,
    title text NOT NULL,
    description text,
    language_id integer NOT NULL,
    original_language_id integer);

ALTER TABLE public.film OWNER TO postgres;

CREATE TABLE public.actor (
    actor_id integer NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL);


ALTER TABLE public.actor OWNER TO postgres;

CREATE TABLE public.film_actor (
    actor_id integer NOT NULL,
    film_id integer NOT NULL);


ALTER TABLE public.film_actor OWNER TO postgres;
