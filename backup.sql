--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6
-- Dumped by pg_dump version 16.5

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
-- Name: admin; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.admin (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256)
);


ALTER TABLE public.admin OWNER TO neondb_owner;

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.admin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_id_seq OWNER TO neondb_owner;

--
-- Name: admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.admin_id_seq OWNED BY public.admin.id;


--
-- Name: course; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.course (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.course OWNER TO neondb_owner;

--
-- Name: course_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.course_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_id_seq OWNER TO neondb_owner;

--
-- Name: course_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.course_id_seq OWNED BY public.course.id;


--
-- Name: game; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.game (
    id integer NOT NULL,
    game_code character varying(6) NOT NULL,
    date timestamp without time zone NOT NULL,
    course_id integer NOT NULL
);


ALTER TABLE public.game OWNER TO neondb_owner;

--
-- Name: game_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.game_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.game_id_seq OWNER TO neondb_owner;

--
-- Name: game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.game_id_seq OWNED BY public.game.id;


--
-- Name: hole; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.hole (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    par integer NOT NULL,
    course_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.hole OWNER TO neondb_owner;

--
-- Name: hole_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.hole_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hole_id_seq OWNER TO neondb_owner;

--
-- Name: hole_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.hole_id_seq OWNED BY public.hole.id;


--
-- Name: localisation_string; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.localisation_string (
    id integer NOT NULL,
    code character varying(100) NOT NULL,
    english_text text NOT NULL,
    french_text text,
    german_text text,
    spanish_text text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.localisation_string OWNER TO neondb_owner;

--
-- Name: localisation_string_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.localisation_string_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.localisation_string_id_seq OWNER TO neondb_owner;

--
-- Name: localisation_string_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.localisation_string_id_seq OWNED BY public.localisation_string.id;


--
-- Name: module_settings; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.module_settings (
    id integer NOT NULL,
    enable_food_drink boolean,
    updated_at timestamp without time zone NOT NULL,
    auto_disable_games boolean DEFAULT false
);


ALTER TABLE public.module_settings OWNER TO neondb_owner;

--
-- Name: module_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.module_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.module_settings_id_seq OWNER TO neondb_owner;

--
-- Name: module_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.module_settings_id_seq OWNED BY public.module_settings.id;


--
-- Name: player; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.player (
    id integer NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public.player OWNER TO neondb_owner;

--
-- Name: player_game; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.player_game (
    id integer NOT NULL,
    player_id integer NOT NULL,
    game_id integer NOT NULL
);


ALTER TABLE public.player_game OWNER TO neondb_owner;

--
-- Name: player_game_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.player_game_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.player_game_id_seq OWNER TO neondb_owner;

--
-- Name: player_game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.player_game_id_seq OWNED BY public.player_game.id;


--
-- Name: player_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.player_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.player_id_seq OWNER TO neondb_owner;

--
-- Name: player_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.player_id_seq OWNED BY public.player.id;


--
-- Name: purchase_details; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.purchase_details (
    id integer NOT NULL,
    games_purchased integer,
    purchase_date date,
    invoice_number character varying(50),
    contact_name character varying(100),
    contact_email character varying(120),
    contact_phone character varying(20),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    notification_sent boolean
);


ALTER TABLE public.purchase_details OWNER TO neondb_owner;

--
-- Name: purchase_details_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.purchase_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchase_details_id_seq OWNER TO neondb_owner;

--
-- Name: purchase_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.purchase_details_id_seq OWNED BY public.purchase_details.id;


--
-- Name: score; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.score (
    id integer NOT NULL,
    player_game_id integer NOT NULL,
    hole_number integer NOT NULL,
    strokes integer NOT NULL
);


ALTER TABLE public.score OWNER TO neondb_owner;

--
-- Name: score_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.score_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.score_id_seq OWNER TO neondb_owner;

--
-- Name: score_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.score_id_seq OWNED BY public.score.id;


--
-- Name: store_settings; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.store_settings (
    id integer NOT NULL,
    language character varying(10) NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.store_settings OWNER TO neondb_owner;

--
-- Name: store_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.store_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.store_settings_id_seq OWNER TO neondb_owner;

--
-- Name: store_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.store_settings_id_seq OWNED BY public.store_settings.id;


--
-- Name: admin id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin ALTER COLUMN id SET DEFAULT nextval('public.admin_id_seq'::regclass);


--
-- Name: course id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course ALTER COLUMN id SET DEFAULT nextval('public.course_id_seq'::regclass);


--
-- Name: game id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.game ALTER COLUMN id SET DEFAULT nextval('public.game_id_seq'::regclass);


--
-- Name: hole id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hole ALTER COLUMN id SET DEFAULT nextval('public.hole_id_seq'::regclass);


--
-- Name: localisation_string id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.localisation_string ALTER COLUMN id SET DEFAULT nextval('public.localisation_string_id_seq'::regclass);


--
-- Name: module_settings id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.module_settings ALTER COLUMN id SET DEFAULT nextval('public.module_settings_id_seq'::regclass);


--
-- Name: player id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player ALTER COLUMN id SET DEFAULT nextval('public.player_id_seq'::regclass);


--
-- Name: player_game id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player_game ALTER COLUMN id SET DEFAULT nextval('public.player_game_id_seq'::regclass);


--
-- Name: purchase_details id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.purchase_details ALTER COLUMN id SET DEFAULT nextval('public.purchase_details_id_seq'::regclass);


--
-- Name: score id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.score ALTER COLUMN id SET DEFAULT nextval('public.score_id_seq'::regclass);


--
-- Name: store_settings id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.store_settings ALTER COLUMN id SET DEFAULT nextval('public.store_settings_id_seq'::regclass);


--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.admin (id, username, email, password_hash) FROM stdin;
1	admin	admin@example.com	scrypt:32768:8:1$bJCjww15BbK2H7RL$d5c091d116becb81ae2a9fe1917a0962f8ecb1bfb0c69c98d38094d28169dbd795613e32abd796328961cb371693f30f9b1e52d68528f497582a5a2c4dfdaee5
\.


--
-- Data for Name: course; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.course (id, name, created_at, updated_at) FROM stdin;
2	Sea View	2025-01-07 16:43:31.815286	2025-01-07 16:43:31.815289
3	Mountain View	2025-01-08 12:03:55.8992	2025-01-08 12:03:55.899204
1	Forest Glen	2025-01-07 16:43:24.605676	2025-01-08 12:05:21.648948
\.


--
-- Data for Name: game; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.game (id, game_code, date, course_id) FROM stdin;
1	450774	2025-01-07 16:45:31.16554	1
2	860487	2025-01-07 16:50:26.863635	1
3	844151	2025-01-07 16:53:46.772586	2
4	308968	2025-01-07 16:59:39.517663	2
5	426218	2025-01-07 17:02:56.139658	1
6	849493	2025-01-07 17:03:24.122169	1
7	750012	2025-01-07 17:11:46.428845	1
8	139078	2025-01-07 17:27:35.812769	1
9	293894	2025-01-07 17:29:06.839626	2
10	733100	2025-01-07 17:30:41.163045	2
11	463911	2025-01-07 17:47:41.422952	2
12	668231	2025-01-07 18:16:41.773792	1
13	956767	2025-01-08 11:56:24.331019	1
14	842590	2025-01-08 12:06:29.048461	2
15	185747	2025-01-08 12:52:12.052087	3
16	106026	2025-01-08 14:13:36.729954	3
17	818525	2025-01-08 14:20:55.546162	2
18	406325	2025-01-08 14:20:56.397708	2
19	613339	2025-01-08 14:23:19.870003	3
20	453033	2025-01-08 14:26:23.370442	3
21	900605	2025-01-08 14:29:33.222537	1
22	203958	2025-01-08 14:32:29.930918	1
23	346017	2025-01-08 14:51:00.33133	3
24	366447	2025-01-08 16:08:47.220439	1
25	738737	2025-01-08 16:13:10.99108	3
26	892962	2025-01-08 16:14:13.927286	1
27	621735	2025-01-08 16:21:46.808278	1
28	342243	2025-01-08 16:28:39.178819	3
29	298348	2025-01-08 16:33:15.157912	2
30	596630	2025-01-08 16:49:49.367153	3
31	787875	2025-01-08 16:52:16.748708	1
32	769048	2025-01-09 09:42:33.259423	3
33	974069	2025-01-09 10:48:03.209504	1
34	537221	2025-01-09 12:00:04.243913	1
\.


--
-- Data for Name: hole; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.hole (id, name, par, course_id, created_at, updated_at) FROM stdin;
2	Hop Scotch	2	1	2025-01-07 16:44:16.748523	2025-01-07 16:44:16.748527
3	Mountain Climb	3	1	2025-01-07 16:44:26.227299	2025-01-07 16:44:26.227304
4	Harbour Point	3	2	2025-01-07 16:44:51.437197	2025-01-07 16:44:51.437201
5	Marine Drive	4	2	2025-01-07 16:45:01.348368	2025-01-07 16:45:01.348372
6	Anchors Away	3	2	2025-01-07 16:45:11.157485	2025-01-07 16:45:11.157488
7	Mermaid's Lair	3	2	2025-01-07 16:55:29.072751	2025-01-07 16:55:29.072755
8	Eagle's Nest	3	3	2025-01-08 12:04:20.791058	2025-01-08 12:04:20.791061
9	Hidden Cave	3	3	2025-01-08 12:04:28.982536	2025-01-08 12:04:28.98254
10	Bear Attack	4	3	2025-01-08 12:04:41.07241	2025-01-08 12:04:41.072414
1	Meteor Shower	2	1	2025-01-07 16:43:59.978435	2025-01-08 12:05:12.039558
\.


--
-- Data for Name: localisation_string; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.localisation_string (id, code, english_text, french_text, german_text, spanish_text, created_at, updated_at) FROM stdin;
4	HomePageTitleLine3	Track your scores, compare your results and eat, drink & be merry!	Suivez vos scores, comparez vos résultats et mangez, buvez et réjouissez-vous !			2025-01-09 10:42:01.313074	2025-01-09 10:42:01.313077
1	HomePageTitleLine1	Royal Putts Brandon	Le Royale Putts Lille	Ze Royal Putts Hamburg	Le Putt Royale Madrid	2025-01-09 10:26:01.083802	2025-01-09 10:53:08.531849
5	HomePageLeftBoxLine1	Track Scores	Suivez les scores			2025-01-09 11:04:07.014198	2025-01-09 11:21:27.681727
6	HomePageLeftBoxLine2	Record your scores hole by hole as you play.	Enregistrez vos scores trou par trou pendant que vous jouez.			2025-01-09 11:04:46.709452	2025-01-09 11:21:53.492287
7	HomePageMiddleBoxLine1	View Results	Consultez les résultats			2025-01-09 11:05:19.697975	2025-01-09 11:22:18.925419
9	HomePageMiddleBoxLine2	Review your past games and progress over time.	Passez en revue vos parties passées et votre progression au fil du temps.			2025-01-09 11:06:57.648144	2025-01-09 11:22:46.101915
8	HomePageRightBoxLine1	Compare Stats	Comparez les statistiques			2025-01-09 11:06:24.474747	2025-01-09 11:23:12.055181
10	HomePageRightBoxLine2	Get insights into your performance with detailed statistics.	Obtenez un aperçu de vos performances grâce à des statistiques détaillées.			2025-01-09 11:07:31.488323	2025-01-09 11:23:40.283809
3	HomePageTitleLine2	Scores 'n' More!	Scores et plus encore!			2025-01-09 10:35:52.376872	2025-01-09 11:24:16.327301
11	NewGame	New Game	Nouvelle Partie			2025-01-09 11:28:01.054497	2025-01-09 11:28:01.054501
12	FindGame	Find Game	Trouvez Une Partie			2025-01-09 12:05:32.31874	2025-01-09 12:08:08.53397
13	OrderFoodMenu	Order Food & Drink	Commandez des Boissons			2025-01-09 12:13:22.76136	2025-01-09 12:13:22.761365
\.


--
-- Data for Name: module_settings; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.module_settings (id, enable_food_drink, updated_at, auto_disable_games) FROM stdin;
1	t	2025-01-09 12:16:38.610957	f
\.


--
-- Data for Name: player; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.player (id, name) FROM stdin;
1	Pete
2	Tom
3	Tad
4	Tod
5	Ted
6	Jill
7	Jen
8	Jack
9	Brad
10	Clive
11	Nelson
12	Bongani
13	Jordan
14	Mariana
15	Bing
16	Nash
17	Helly
18	Skelly
19	Glen
20	Bill
21	Bob
22	Will
23	Sam
24	Jim
25	Jon
26	Fred
27	Freda
28	Tim
29	ghgg
30	dfgsf
31	sdghdf
32	hj
33	col
34	hgsdfg
35	sigh
36	xbfg
37	dgf
38	dg
39	Tit
40	Fff
41	Gill
42	Bingo
43	JK
44	PT
45	Julie
46	Richard
47	Alf
48	hhhgfd
49	duh
\.


--
-- Data for Name: player_game; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.player_game (id, player_id, game_id) FROM stdin;
1	1	1
2	2	1
3	3	2
4	4	2
5	5	2
6	6	3
7	7	3
8	8	3
9	9	4
10	10	4
11	11	5
12	12	5
13	13	6
14	14	6
15	15	7
16	16	7
17	17	8
18	18	8
19	19	9
20	20	9
21	6	10
22	20	10
23	19	11
24	21	11
25	22	12
26	23	12
27	24	13
28	25	13
29	26	14
30	27	14
31	28	15
32	2	15
33	20	16
34	5	16
35	5	17
36	20	17
37	5	18
38	20	18
39	29	21
40	30	22
41	31	22
42	32	22
43	5	23
44	20	23
45	24	24
46	33	24
47	34	25
48	35	25
49	36	26
50	37	27
51	38	27
52	2	28
53	39	28
54	40	29
55	41	29
56	42	29
57	13	30
58	13	31
59	43	32
60	44	32
61	45	33
62	46	33
63	47	33
64	48	34
65	49	34
\.


--
-- Data for Name: purchase_details; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.purchase_details (id, games_purchased, purchase_date, invoice_number, contact_name, contact_email, contact_phone, created_at, updated_at, notification_sent) FROM stdin;
1	13	2023-09-25	45454	Royal Putts Ltd	richardstanden+royalputts@gmail.com	07760165889	2025-01-08 11:55:32.777949	2025-01-08 16:30:05.753932	t
\.


--
-- Data for Name: score; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.score (id, player_game_id, hole_number, strokes) FROM stdin;
1	1	1	2
2	2	1	1
3	6	1	1
4	7	1	2
5	8	1	2
6	6	2	1
7	7	2	3
8	8	2	3
9	6	3	2
10	7	3	3
11	8	3	4
12	6	4	2
13	7	4	3
14	8	4	3
15	9	1	5
16	10	1	3
17	9	2	2
18	10	2	3
19	9	3	3
20	10	3	4
21	9	4	2
22	10	4	1
23	11	1	3
24	12	1	4
25	11	2	3
26	12	2	2
27	11	3	1
28	12	3	2
29	13	1	3
30	14	1	2
31	13	2	1
32	14	2	2
33	13	3	4
34	14	3	1
35	15	1	2
36	16	1	1
37	15	2	8
38	16	2	2
39	15	3	2
40	16	3	2
41	17	1	2
42	18	1	2
43	17	2	2
44	18	2	3
45	17	3	1
46	18	3	2
47	21	1	2
48	22	1	3
49	21	2	1
50	22	2	2
51	21	3	2
52	22	3	3
53	21	4	6
54	22	4	5
55	25	1	1
56	26	1	2
57	25	2	3
58	26	2	1
59	27	1	1
60	28	1	2
61	27	2	1
62	28	2	3
63	27	3	2
64	28	3	2
65	29	1	1
66	30	1	3
67	29	2	3
68	30	2	4
69	29	3	1
70	30	3	2
71	29	4	2
72	30	4	3
73	31	1	2
74	32	1	6
75	31	2	5
76	32	2	1
77	31	3	6
78	32	3	2
79	33	1	2
80	34	1	2
81	33	2	1
82	34	2	1
83	33	3	1
84	34	3	1
85	37	1	6
86	38	1	5
87	37	2	1
88	38	2	2
89	37	3	2
90	38	3	2
91	37	4	2
92	38	4	2
93	39	1	1
94	40	1	1
95	41	1	2
96	42	1	3
97	40	2	3
98	41	2	3
99	42	2	1
100	40	3	1
101	41	3	3
102	42	3	1
103	43	1	2
104	44	1	2
105	50	1	0
106	51	1	0
107	52	1	5
108	53	1	3
109	52	2	4
110	53	2	1
111	52	3	7
112	53	3	2
113	54	1	2
115	54	2	2
116	55	2	1
117	54	3	5
118	55	3	1
119	54	4	2
120	55	4	1
114	55	1	10
121	57	1	2
122	57	2	3
123	59	1	1
124	60	1	2
125	59	2	3
126	60	2	1
127	59	3	0
128	60	3	0
129	61	1	1
130	62	1	2
131	61	2	2
132	62	2	2
133	61	3	1
134	62	3	2
135	63	1	2
\.


--
-- Data for Name: store_settings; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.store_settings (id, language, updated_at) FROM stdin;
1	fr	2025-01-09 11:24:24.278759
\.


--
-- Name: admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.admin_id_seq', 1, true);


--
-- Name: course_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.course_id_seq', 3, true);


--
-- Name: game_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.game_id_seq', 34, true);


--
-- Name: hole_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.hole_id_seq', 10, true);


--
-- Name: localisation_string_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.localisation_string_id_seq', 13, true);


--
-- Name: module_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.module_settings_id_seq', 1, true);


--
-- Name: player_game_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.player_game_id_seq', 65, true);


--
-- Name: player_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.player_id_seq', 49, true);


--
-- Name: purchase_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.purchase_details_id_seq', 1, true);


--
-- Name: score_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.score_id_seq', 135, true);


--
-- Name: store_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.store_settings_id_seq', 1, true);


--
-- Name: admin admin_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_email_key UNIQUE (email);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: admin admin_username_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_username_key UNIQUE (username);


--
-- Name: course course_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course
    ADD CONSTRAINT course_name_key UNIQUE (name);


--
-- Name: course course_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course
    ADD CONSTRAINT course_pkey PRIMARY KEY (id);


--
-- Name: game game_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_pkey PRIMARY KEY (id);


--
-- Name: hole hole_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hole
    ADD CONSTRAINT hole_pkey PRIMARY KEY (id);


--
-- Name: localisation_string localisation_string_code_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.localisation_string
    ADD CONSTRAINT localisation_string_code_key UNIQUE (code);


--
-- Name: localisation_string localisation_string_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.localisation_string
    ADD CONSTRAINT localisation_string_pkey PRIMARY KEY (id);


--
-- Name: module_settings module_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.module_settings
    ADD CONSTRAINT module_settings_pkey PRIMARY KEY (id);


--
-- Name: player_game player_game_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player_game
    ADD CONSTRAINT player_game_pkey PRIMARY KEY (id);


--
-- Name: player player_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player
    ADD CONSTRAINT player_pkey PRIMARY KEY (id);


--
-- Name: purchase_details purchase_details_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.purchase_details
    ADD CONSTRAINT purchase_details_pkey PRIMARY KEY (id);


--
-- Name: score score_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.score
    ADD CONSTRAINT score_pkey PRIMARY KEY (id);


--
-- Name: store_settings store_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.store_settings
    ADD CONSTRAINT store_settings_pkey PRIMARY KEY (id);


--
-- Name: ix_game_game_code; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_game_game_code ON public.game USING btree (game_code);


--
-- Name: game game_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.game
    ADD CONSTRAINT game_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course(id);


--
-- Name: hole hole_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.hole
    ADD CONSTRAINT hole_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.course(id);


--
-- Name: player_game player_game_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player_game
    ADD CONSTRAINT player_game_game_id_fkey FOREIGN KEY (game_id) REFERENCES public.game(id);


--
-- Name: player_game player_game_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.player_game
    ADD CONSTRAINT player_game_player_id_fkey FOREIGN KEY (player_id) REFERENCES public.player(id);


--
-- Name: score score_player_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.score
    ADD CONSTRAINT score_player_game_id_fkey FOREIGN KEY (player_game_id) REFERENCES public.player_game(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

