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

## Plan de publicacións

- Unha publicación ao día, ás **19:00 hora de España**.
- Alternar reels (mínimo 3 por semana), carruseis e fotos.
- Mestura semanal orientativa: 2 festival/ópera, 2 Cedeira, 1 Xeoparque, 1 detrás das cámaras ou alumnado, 1 libre (curiosidades de ópera, repertorio, cantantes).
- Os mellores reels combinan música do festival con paisaxes de Cedeira ou do Xeoparque.

## Vídeos

- Reels verticais 1080x1920, de 15 a 45 segundos, montados con ffmpeg.
- Un texto forte nos primeiros 2 segundos e subtítulos cando haxa voz ou texto importante.
- Audio só das gravacións propias do festival.

## Fluxo de traballo

- Cando Fran diga **"prepara a semana"**: crear en `publicacions/AAAA-MM-DD/` cada publicación co seu arquivo (imaxe, carrusel ou vídeo) e un `texto.md` co texto, os hashtags, os créditos e a hora.
- Non publicar nada sen aprobación previa de Fran. Cando diga **"aprobado"**, marcar esa semana como lista (ex.: crear un ficheiro `APROBADO` na carpeta da semana).
- Script de publicación diaria coa API oficial de Instagram (Instagram API with Instagram Login). Token e ID de usuario en `.env` (`IG_ACCESS_TOKEN`, `IG_USER_ID`).
- A API precisa URLs públicas: subir primeiro os arquivos por FTP a `ariacedeira.gal/ig/` (credenciais FTP tamén en `.env`) e borralos despois de publicar.
- Publicación automática con GitHub Actions para que funcione aínda co ordenador apagado. Token en GitHub Secrets, nunca no código.
- O script debe renovar o token antes de que caduque (cada 60 días).
- Cada domingo revisar as estatísticas da semana e propor melloras a Fran.

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
  internet/            — descargas con licenza libre + creditos.md
publicacions/
  AAAA-MM-DD/           — unha carpeta por semana preparada
scripts/               — scripts de publicación, renovación de token, estatísticas
.github/workflows/      — automatización de publicación diaria
_orixinais/             — arquivos orixinais sen procesar (zips, etc.)
.env                    — segredos (NON subir a git): IG_ACCESS_TOKEN, IG_USER_ID, FTP_*
```
