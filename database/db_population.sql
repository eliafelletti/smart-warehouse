--
-- PostgreSQL database dump
--

\restrict y5gwaHYUQiwqlXGhRTS5o5u35G3tZr5ckumEF6CAeGRNDdoXleMcQD0J4P4ADlD

-- Dumped from database version 13.22 (Debian 13.22-1.pgdg13+1)
-- Dumped by pg_dump version 13.22 (Debian 13.22-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accesslogs; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.accesslogs (
    log_id uuid NOT NULL,
    user_id integer,
    sector_id integer,
    "timestamp" timestamp with time zone DEFAULT now(),
    access_granted boolean NOT NULL
);


ALTER TABLE public.accesslogs OWNER TO "user";

--
-- Name: inventory; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.inventory (
    product_id integer NOT NULL,
    sector_id integer NOT NULL,
    quantity integer DEFAULT 0 NOT NULL,
    CONSTRAINT check_positive_stock CHECK ((quantity >= 0))
);


ALTER TABLE public.inventory OWNER TO "user";

--
-- Name: products; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    name text NOT NULL,
    reorder_threshold integer DEFAULT 10,
    supplier_info text
);


ALTER TABLE public.products OWNER TO "user";

--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.products_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_product_id_seq OWNER TO "user";

--
-- Name: products_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.products_product_id_seq OWNED BY public.products.product_id;


--
-- Name: sectors; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.sectors (
    sector_id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.sectors OWNER TO "user";

--
-- Name: sectors_sector_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.sectors_sector_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sectors_sector_id_seq OWNER TO "user";

--
-- Name: sectors_sector_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.sectors_sector_id_seq OWNED BY public.sectors.sector_id;


--
-- Name: stockmovementslog; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.stockmovementslog (
    log_id uuid NOT NULL,
    product_id integer,
    sector_id integer,
    user_id integer,
    quantity integer NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now()
);


ALTER TABLE public.stockmovementslog OWNER TO "user";

--
-- Name: supplierorders; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.supplierorders (
    order_id uuid NOT NULL,
    product_id integer,
    user_id integer,
    quantity integer NOT NULL,
    timestamp_created timestamp with time zone DEFAULT now()
);


ALTER TABLE public.supplierorders OWNER TO "user";

--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username text NOT NULL,
    badge_id text,
    role text
);


ALTER TABLE public.users OWNER TO "user";

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO "user";

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: usersectorpermissions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.usersectorpermissions (
    user_id integer NOT NULL,
    sector_id integer NOT NULL
);


ALTER TABLE public.usersectorpermissions OWNER TO "user";

--
-- Name: products product_id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products ALTER COLUMN product_id SET DEFAULT nextval('public.products_product_id_seq'::regclass);


--
-- Name: sectors sector_id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sectors ALTER COLUMN sector_id SET DEFAULT nextval('public.sectors_sector_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: accesslogs; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.accesslogs (log_id, user_id, sector_id, "timestamp", access_granted) FROM stdin;
1dfa8f2b-1be5-4b93-9405-759c9930282f	1	2	2025-11-08 10:52:23.749059+00	t
273977e2-f79d-476e-8a1d-e73cf0e2d22a	1	1	2025-11-14 18:08:59.591193+00	t
2f371a45-1809-4dce-8eab-674f0d8011a3	1	2	2025-11-14 18:11:34.598296+00	t
c34bd5ac-1012-43a1-a826-93f24a78e0ab	1	2	2025-11-14 18:21:10.23502+00	t
06ad7030-3c2c-45f8-b9cb-eda11cb91b08	2	5	2025-11-14 18:22:36.805253+00	f
62c9c585-1657-4535-92ca-d8dbd88a1b66	1	2	2025-11-14 18:30:34.921106+00	t
30921c1d-ebe6-4342-8a59-058e4c74a9f4	1	1	2025-11-15 10:54:52.070825+00	t
bc007997-7af7-4b9a-a02e-4ebd3311efd0	1	4	2025-11-15 15:04:44.453175+00	t
a7c368fb-1aa6-45fc-ba5e-e8905904acd6	1	2	2025-11-15 15:08:42.956324+00	t
b0d8bd90-7198-4a8d-a863-291dfde82b2c	1	5	2025-11-15 15:15:53.619076+00	t
f80ab5e6-af5e-4a61-86cd-03c893b94668	1	5	2025-11-15 15:16:33.558655+00	t
72301ae8-7364-4675-92df-3c4d074f0e86	1	5	2025-11-19 17:11:17.2213+00	t
80a15209-d4dd-4aa5-a7aa-0c66ec392698	2	5	2025-11-19 17:13:23.086808+00	f
0df27b59-2b2f-4e06-a28a-e632e2be82f5	1	4	2026-03-02 14:49:01.336462+00	t
440d359d-f779-4430-98bd-e90c376d4002	2	5	2026-03-02 14:51:27.61095+00	f
149b61f6-cf75-4556-a8bc-2d976a32450d	1	5	2026-03-03 16:16:40.569532+00	t
f89ded16-dfe1-4b77-8926-c932ed003021	2	1	2026-03-03 16:36:27.604414+00	f
acc755b7-0bb0-49b1-94dc-6a890a7976f6	1	1	2026-03-03 16:36:53.237688+00	t
3342f489-f96e-4efc-a6bb-6f6a0b852cb4	2	1	2026-03-10 14:58:39.440708+00	f
c9314248-a25e-46a4-a349-4e97c9cc0c58	2	2	2026-03-10 14:59:36.956459+00	t
abf53aa1-43f9-4a10-889f-04437fde8d5c	2	2	2026-03-10 16:56:03.341183+00	t
96453b47-5d3e-4497-b3f5-acf6c6c2dbc6	1	3	2026-03-10 17:29:57.791583+00	t
ef7a4430-262d-4ddc-90fe-a1ae84c0f6b2	2	4	2026-04-02 13:48:58.028526+00	f
193105e9-9418-4826-9e8e-6982572b64ee	2	3	2026-04-02 14:48:52.43865+00	t
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.inventory (product_id, sector_id, quantity) FROM stdin;
5	5	60
7	4	100
9	1	50
4	5	90
2	1	175
3	4	5
7	2	40
6	5	105
8	4	90
10	5	20
1	1	15
3	2	55
8	2	35
5	3	5
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.products (product_id, name, reorder_threshold, supplier_info) FROM stdin;
1	lamiera	20	Acciaierie S.p.A.
2	mattone	100	Edilizia Srl
3	sabbia (sacco 25kg)	50	Forniture Edili Rossi
4	barre di ferro (12mm)	40	Acciaierie S.p.A.
5	tubi PVC (DN100)	30	Plastica e Tubi Srl
6	rubinetti (modello A)	15	Idraulica Bianchi
7	cemento (sacco 25kg)	50	Forniture Edili Rossi
8	ghiaia (sacco 25kg)	50	Forniture Edili Rossi
9	piastrelle (mq)	10	Ceramiche Verdi
10	pannelli isolanti (mq)	25	Isolanti Srl
\.


--
-- Data for Name: sectors; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.sectors (sector_id, name) FROM stdin;
1	Scaffale A-1
2	Area Carico
3	Area Prelievo
4	Zona Materiali Sfusi
5	Scaffale B-1
\.


--
-- Data for Name: stockmovementslog; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.stockmovementslog (log_id, product_id, sector_id, user_id, quantity, "timestamp") FROM stdin;
1a28638c-6901-4da5-ba48-ed87ec0fb211	1	1	1	-10	2025-11-08 10:24:51.352106+00
9fc4d2df-e6d6-41d0-bd6b-e3cd8f109ffa	2	1	1	15	2025-11-08 10:25:42.009228+00
096b4a44-47df-4e17-b2ca-4df915721f95	4	5	1	10	2025-11-13 10:43:28.03591+00
ae700975-0ccd-4016-973c-3d1787042623	1	1	1	-5	2025-11-14 18:08:59.591193+00
87601c5a-5b1e-4291-8102-1ffc0a52b0fb	7	2	1	15	2025-11-14 18:11:34.582475+00
c9fe2252-2aca-4311-bbca-dcdf4294fa43	7	2	1	50	2025-11-14 18:21:10.216631+00
4561258c-5788-41be-8585-9d76d0f8cf37	7	2	1	-5	2025-11-14 18:30:34.904242+00
65108f2a-4e60-4ecf-b0f1-cfea3234e72c	2	1	1	-40	2025-11-15 10:54:52.039629+00
04babd64-aa2a-4099-a2ea-00ffbd0b928a	3	4	1	-95	2025-11-15 15:04:44.420388+00
dac2578a-8b16-499f-af27-351cdaff1c0d	7	2	1	-5	2025-11-15 15:08:42.939135+00
578b4d80-48b7-48ca-98d9-f60c35739f21	6	5	1	-20	2025-11-15 15:15:53.599661+00
5ec8236d-e6fa-457f-a4ab-a38624bc569e	6	5	1	100	2025-11-15 15:16:33.543357+00
a0e1bd5a-8a63-451c-a285-136cf192bbb7	6	5	1	-5	2025-11-19 17:11:17.221334+00
237b0186-2882-4ed0-a67a-7cdb430a6426	8	4	1	-10	2026-03-02 14:49:01.336459+00
0c084299-be5c-4799-8e9f-3ff866db0670	10	5	1	-20	2026-03-03 16:16:40.56959+00
227cbf09-9c25-420b-8160-14aa9854706c	1	1	1	-20	2026-03-03 16:36:53.220079+00
267ccb09-0447-4b88-84fa-0e0b2363ba54	3	2	2	55	2026-03-10 14:59:36.940921+00
6f35eca5-6235-4b33-afb4-e2917f0e11bb	8	2	2	35	2026-03-10 16:56:03.318898+00
df76563f-dec4-4b56-a7df-622d78798542	5	3	1	40	2026-03-10 17:29:57.773573+00
5df07aa6-1768-48ef-bb73-6578715fd076	5	3	2	-35	2026-04-02 14:48:52.427898+00
\.


--
-- Data for Name: supplierorders; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.supplierorders (order_id, product_id, user_id, quantity, timestamp_created) FROM stdin;
cdf052ae-6ce1-4911-84c4-7905d0cbd749	3	1	15	2025-11-07 15:27:24.551259+00
0626978e-46c4-480d-8855-1b4378bb8e69	3	1	100	2025-11-15 15:04:44.437636+00
2d391832-519a-4afe-8762-de5cf0f81b65	6	1	100	2025-11-15 15:15:53.601734+00
641fe04e-6ee6-437f-9993-15d8342cee65	9	1	20	2026-03-02 14:52:22.839917+00
6c0fcad6-8b85-41eb-aa8b-05d5c606d94d	10	1	100	2026-03-03 16:16:40.56957+00
2179cd5c-7a55-4a36-b930-ccb087a24920	1	0	100	2026-03-03 16:36:53.226128+00
710d64d1-0c2e-40ae-90bb-dc79b90f084e	4	1	90	2026-03-10 15:27:22.492582+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.users (user_id, username, badge_id, role) FROM stdin;
1	elia	A-123	admin
2	operatore_1	B-456	operatore
0	auto_reordering_sys	SYS-000	admin
\.


--
-- Data for Name: usersectorpermissions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.usersectorpermissions (user_id, sector_id) FROM stdin;
1	1
1	2
1	3
1	4
1	5
2	2
2	3
\.


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.products_product_id_seq', 10, true);


--
-- Name: sectors_sector_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.sectors_sector_id_seq', 5, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.users_user_id_seq', 2, true);


--
-- Name: accesslogs accesslogs_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accesslogs
    ADD CONSTRAINT accesslogs_pkey PRIMARY KEY (log_id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (product_id, sector_id);


--
-- Name: products products_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_name_key UNIQUE (name);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: sectors sectors_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sectors
    ADD CONSTRAINT sectors_name_key UNIQUE (name);


--
-- Name: sectors sectors_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.sectors
    ADD CONSTRAINT sectors_pkey PRIMARY KEY (sector_id);


--
-- Name: stockmovementslog stockmovementslog_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stockmovementslog
    ADD CONSTRAINT stockmovementslog_pkey PRIMARY KEY (log_id);


--
-- Name: supplierorders supplierorders_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supplierorders
    ADD CONSTRAINT supplierorders_pkey PRIMARY KEY (order_id);


--
-- Name: users users_badge_id_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_badge_id_key UNIQUE (badge_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: usersectorpermissions usersectorpermissions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usersectorpermissions
    ADD CONSTRAINT usersectorpermissions_pkey PRIMARY KEY (user_id, sector_id);


--
-- Name: accesslogs accesslogs_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accesslogs
    ADD CONSTRAINT accesslogs_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES public.sectors(sector_id);


--
-- Name: accesslogs accesslogs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.accesslogs
    ADD CONSTRAINT accesslogs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: inventory inventory_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: inventory inventory_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES public.sectors(sector_id);


--
-- Name: stockmovementslog stockmovementslog_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stockmovementslog
    ADD CONSTRAINT stockmovementslog_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: stockmovementslog stockmovementslog_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stockmovementslog
    ADD CONSTRAINT stockmovementslog_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES public.sectors(sector_id);


--
-- Name: stockmovementslog stockmovementslog_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.stockmovementslog
    ADD CONSTRAINT stockmovementslog_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: supplierorders supplierorders_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supplierorders
    ADD CONSTRAINT supplierorders_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: supplierorders supplierorders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supplierorders
    ADD CONSTRAINT supplierorders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: usersectorpermissions usersectorpermissions_sector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usersectorpermissions
    ADD CONSTRAINT usersectorpermissions_sector_id_fkey FOREIGN KEY (sector_id) REFERENCES public.sectors(sector_id);


--
-- Name: usersectorpermissions usersectorpermissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usersectorpermissions
    ADD CONSTRAINT usersectorpermissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

\unrestrict y5gwaHYUQiwqlXGhRTS5o5u35G3tZr5ckumEF6CAeGRNDdoXleMcQD0J4P4ADlD

