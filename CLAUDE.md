# Xestión de Instagram — @operastudiocedeira

Conta de Instagram do **Opera Studio Cedeira / Festival de Ópera e Música de Cámara CedeirART**, organizado por Fran Pérez.
Web: ariacedeira.gal e cedeirart.gal.

## Obxectivo

Chegar a novos públicos e promocionar tres cousas á vez:
1. O festival e o Opera Studio: ópera, música de cámara, alumnado, concertos.
2. Cedeira como destino: vila mariñeira, praias, porto, gastronomía, San Andrés de Teixido, Serra da Capelada.
3. O Xeoparque Mundial UNESCO Cabo Ortegal: cantís, rochas, paisaxe e xeoloxía.

Mensaxe de fondo: **"ven a Cedeira a vivir a ópera nun lugar único"**.

## Ton e idioma

- Textos en galego, cunha versión breve en castelán debaixo. Engade inglés cando o contido sexa turístico.
- Próximo, culto pero non elitista. Que achegue a ópera a quen nunca foi.

## Material dispoñible

- `material/fotos/opera/` e `material/fotos/cedeira/`: fotos propias.
- `material/videos/`: gravacións propias do festival, con autorización firmada dos músicos. Úsase libremente o seu audio e os seus clips para os reels (extraer con ffmpeg).
- Imaxes e vídeos de Cedeira e do Xeoparque Cabo Ortegal: buscar en internet, só con licenzas que permitan uso promocional e modificación:
  - Válidas: dominio público, CC0, CC BY, CC BY-SA, licenza Unsplash e licenza Pexels.
  - Non válidas: calquera licenza NC (non comercial) ou ND (sen obras derivadas), nin imaxes sen licenza clara.
  - Fontes preferentes: Wikimedia Commons, Unsplash e Pexels.
  - Descargar en `material/internet/` e anotar cada unha en `material/internet/creditos.md` co arquivo, autor, licenza e URL orixinal.
  - Cando a licenza pida atribución (CC BY, CC BY-SA), poñer o crédito ao final do texto da publicación (ex.: "📷 Autor / CC BY-SA 4.0 / Wikimedia Commons").
  - Non usar imaxes onde se recoñezan caras de persoas.
- Música libre para os reels de imaxes de Cedeira/Xeoparque (non gravacións do festival): só con licenzas que permitan uso comercial/promocional:
  - Fontes preferentes: YouTube Audio Library, Pixabay Music, Free Music Archive (filtrando por CC BY/CC0).
  - Mesmas regras de licenza ca as imaxes (válido: dominio público, CC0, CC BY; non válido: NC, ND, sen licenza clara).
  - Anotar tamén en `material/internet/creditos.md` (arquivo, autor/música, licenza, URL orixinal).
  - Cando a licenza pida atribución, engadir o crédito ao final do texto da publicación.

## Plan de publicacións

- **Dúas publicacións ao día**: unha ás **13:00** (Cedeira ou Xeoparque) e outra ás **19:00** (festival/ópera) hora de España. (Cambio decidido o 2026-10-01; a primeira semana preparada antes desa data segue co formato antigo de 1 publicación/día.)
- Alternar reels (mínimo 3 por semana), carruseis e fotos.
- Intercalar tamén reels feitos con fotos de Cedeira/Xeoparque + música libre (non só vídeo do festival) para promocionar o destino.
- Mestura semanal orientativa por franxa: a franxa das 19:00 adoita ser festival/ópera; a franxa das 13:00 adoita ser Cedeira ou Xeoparque, con algún día de detrás das cámaras/alumnado ou contido libre (curiosidades de ópera, repertorio, cantantes) intercalado.
- Os mellores reels combinan música do festival con paisaxes de Cedeira ou do Xeoparque.
- **Regra importante (2026-10-01)**: o contido de territorio (Cedeira/Xeoparque) NUNCA vai só de turismo xenérico — sempre ten que ligar co festival no texto (ex. "a vila que acolle a ópera", "ven vivir a ópera aquí"). Nos reels de fotos de territorio, mesturar sempre algunha foto do festival entre as de paisaxe (usar `scripts/make_photo_reel.sh`).

## Vídeos

- Reels de 15 a 45 segundos, montados con ffmpeg, mantendo a resolución e proporción orixinais do vídeo de orixe (sen recortalo nin engadir bandas difuminadas arriba/abaixo — así quedou acordado o 2026-10-01 tras a primeira proba).
- Un texto forte nos primeiros 2 segundos e un pé de texto permanente coa peza/festival.
- Audio das gravacións propias do festival (para reels de ópera) ou música libre licenciada (para reels de imaxes de Cedeira/Xeoparque).

## Fluxo de traballo

- Cando Fran diga **"prepara a semana"**: crear cada publicación co seu arquivo (imaxe, carrusel ou vídeo) e un `texto.md` co texto, os hashtags, os créditos e a hora:
  - Formato novo (2 publicacións/día, dende 2026-10-01): `publicacions/AAAA-MM-DD/13h-<categoría>/` e `publicacions/AAAA-MM-DD/19h-<categoría>/`.
  - A primeira semana (2026-09-30 a 2026-10-06) quedou co formato antigo dunha soa carpeta `publicacions/AAAA-MM-DD/` — non facía falla migrala.
- Non publicar nada sen aprobación previa de Fran. Cando diga **"aprobado"**, crear un ficheiro `APROBADO` en cada carpeta de publicación lista (do día ou da franxa horaria, segundo o formato).
- Script de publicación (`scripts/publish_daily.py`) coa API oficial de Instagram (Instagram API with Instagram Login). Token e ID de usuario en `.env` (`IG_ACCESS_TOKEN`, `IG_USER_ID`).
- A API precisa URLs públicas: os arquivos xa están no repositorio de GitHub (público) e sírvense directamente dende `raw.githubusercontent.com` — non se usa FTP para isto (o hosting de ariacedeira.gal bloquea conexións FTP dende IPs de datacenter/nube, comprobado o 2026-09-30). As credenciais FTP (`.env`) quedan gardadas para outros usos puntuais, non para a publicación automática.
- Publicación automática con GitHub Actions (`.github/workflows/daily-publish.yml`) para que funcione aínda co ordenador apagado. Token en GitHub Secrets, nunca no código.
- O script de renovación (`scripts/renew_token.py`, workflow `renew-token.yml`) renova o token cada luns, antes de que caduque (cada 60 días).
- Cada domingo revisar as estatísticas da semana e propor melloras a Fran (pendente de configurar como tarefa programada).

## Estratexia para novos públicos

- Hashtags mesturando ópera, música clásica, turismo en Galicia e xeoparques. Máximo 8 e variados.
- Etiquetar localizacións reais (Cedeira, Cabo Ortegal, San Andrés de Teixido...).
- Propor colaboracións e mencións con contas de turismo (Concello de Cedeira, Turismo de Galicia, Xeoparque Cabo Ortegal) e con cantantes e músicos.

## Límites

- Non inventar datos, datas, nomes nin prezos: se falta algo, preguntar a Fran.
- Non publicar caras de alumnado ou público sen que Fran confirme que hai permiso, e nunca de menores.
- Non publicar nada sen que Fran diga "aprobado" para esa semana.

## Datos do próximo festival

Aínda non se sabe. Preguntar a Fran cando se vaia achegando a data.

## Estrutura do proxecto

```
material/
  fotos/opera/       — fotos propias do festival (477 fotos xa importadas)
  fotos/cedeira/      — fotos propias de Cedeira
  videos/             — gravacións propias do festival (autorización firmada)
                         + autorizacions.md (índice de participantes/autorizacións)
  internet/            — descargas con licenza libre (fotos e música) + creditos.md
publicacions/
  AAAA-MM-DD/                     — formato antigo (1 publicación/día, só semana 1)
  AAAA-MM-DD/13h-<categoría>/     — formato novo, publicación do mediodía
  AAAA-MM-DD/19h-<categoría>/     — formato novo, publicación da tarde
scripts/
  publish_daily.py      — publica (lé APROBADO/PUBLICADO, chama á API de Instagram)
  renew_token.py         — renova o IG_ACCESS_TOKEN (chámao renew-token.yml cada luns)
  make_reel.sh            — monta un reel con ffmpeg (recorte de vídeo + texto, resolución orixinal)
  make_photo_reel.sh       — monta un reel de fotos (Ken Burns) + música libre, para territorio
  check_token.sh           — comproba que o token funciona
  exchange_token.sh         — troca un token curto por un de longa duración (setup manual)
.github/workflows/
  daily-publish.yml     — publica ás 13:00 e 19:00 (hora España) + workflow_dispatch manual
  renew-token.yml         — renova o token cada luns
_orixinais/             — arquivos orixinais sen procesar (zips, etc.) — NON vai a git
.env                    — segredos (NON vai a git): IG_ACCESS_TOKEN, IG_USER_ID, APP_ID,
                           APP_SECRET, FTP_* (FTP gardado para outros usos, non a publicación)

Repositorio de GitHub: github.com/panxolio-ai/instagram-cedeirart (PÚBLICO dende 2026-10-01,
necesario para que raw.githubusercontent.com sirva os arquivos; os Secrets seguen protexidos).
```
