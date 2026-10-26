# Kubeløser

Tag seks billeder af en rubikskube, ret evt. farverne, og få en trin-for-trin løsning. Hele appen er én HTML-fil (`index.html`), der kører i browseren. Billederne forlader aldrig enheden.

## Sådan virker den

1. **Seks billeder.** Appen guider gennem forside, højre, bagside, venstre, top og bund. På en telefon åbner knappen kameraet; ellers kan man vælge et billede.
2. **Farveaflæsning.** Et gitter lægges over billedet (kan flyttes, skaleres og drejes). Farven aflæses som medianen i midten af hvert af de ni felter.
3. **Klassificering.** De seks midterfelter definerer de seks farver. Alle 48 øvrige felter fordeles med den ungarske metode, så hver farve får præcis 8. Lyset regnes ud for hvert billede (log-farverum), så forskelle i lysstyrke og farvestik mellem billederne ikke ødelægger resultatet. Felter, appen er usikker på, får en prik.
4. **Kontrol.** Før løsning tjekkes antal pr. farve, om hvert hjørne og hver kant findes, hjørnernes og kanternes vending og permutationens paritet. Terninger, der ikke kan løses, afvises med en forklaring.
5. **Løsning.** [cubejs](https://github.com/ldez/cubejs) (Kociemba, højst 22 træk) kører i en Web Worker og varmes op, mens man tager billeder. Hvert træk vises på terningen forfra og på de seks sider foldet ud.

## Filer

| Fil | Indhold |
| --- | --- |
| `template.html` | Hele appen (HTML, CSS, JS). Biblioteket indsættes ved build. |
| `build.py` | Bygger `index.html` (til brug) og `index.test.html` (med test-hook). |
| `vendor/cubejs/` | cubejs 1.3.2 (MIT), uændret. |
| `tests/` | Playwright-tests, se nedenfor. |

## Byg og test

```sh
python3 build.py                   # skriver index.html og index.test.html
pip install playwright pillow && playwright install chromium
python3 tests/logic.py             # kontrollen mod 600 tilfældige og 400 ødelagte terninger
python3 tests/e2e.py 1             # seks syntetiske fotos -> aflæsning -> løsning -> løst terning
python3 tests/e2e.py 1 --hard      # samme med dårligt lys, farvestik, genskær og forskydning
python3 tests/final.py             # reserveløsning uden Web Worker, og ret-en-farve-flowet
```

`e2e.py` kræver Node (til at lave en tilfældig blandet terning). Testene bruger syntetiske billeder, ikke rigtige fotos.

## Fotoretning

Billedet af hver side læses række for række og passer direkte til Kociembas felt-rækkefølge (U, R, F, D, L, B):

- Forside, højre, bagside, venstre: drej hele terningen om lodret akse, toppen peger opad.
- Top: tip toppen hen mod dig, så bagsiden er øverst i billedet.
- Bund: tip bunden hen mod dig, så forsiden er øverst i billedet.

Farveskemaet er ligegyldigt. Det er midterfeltet på hvert billede, der afgør, hvilken side en farve hører til.

## Kendte begrænsninger

- Løsningen er den korteste, ikke en begyndermetode.
- Aflæsningen er testet med syntetiske billeder. Rigtige fotos med stærk perspektivforvrængning eller skygger kan give flere usikre felter, som man så retter i hånden.

## Licens

Appen: MIT. `vendor/cubejs`: MIT, se `vendor/cubejs/LICENSE`.
