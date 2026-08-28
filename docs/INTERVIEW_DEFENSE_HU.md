# Interjúvédési útmutató – magyar

## A projekt egy mondatban

Egy hibrid, ember által felügyelt AI Service Desk Copilotot építettem, amely egy magyarázható klasszikus ML-modellel P1–P4 prioritást becsül, majd jóváhagyott runbookokból visszakeresett bizonyítékokra támaszkodva, verziózott és tesztelt prompttal biztonságos első reakciótervet készít.

## 30 másodperces bemutatás

> Az IT-üzemeltetési és ITSM-tapasztalatomat kötöttem össze az AI/ML és prompt engineering tudásommal. A rendszer szintetikus, reprodukálható service desk adatokon tanított NLP-modellel becsüli a ticket prioritását, majd egy kontrollált RAG-réteg releváns runbookokat keres, és strukturált, forráshivatkozásos első reakciótervet állít elő. A rendszer redaktálja az érzékeny adatokat, figyeli a prompt injection jeleit, validálja a kimenetet, és soha nem enged autonóm végrehajtást. A lényeg nem egy látványos chatbot, hanem egy mérhető, auditálható és üzemeltethető AI-szolgáltatás terve.

## 90 másodperces bemutatás

> A kiinduló üzleti probléma az volt, hogy a ticketprioritás és az első reakció minősége elemzőnként eltérhet. Egy elnézett P1 súlyos, de a túl sok P1 riasztási fáradtságot okoz. Ezért kettéválasztottam a problémát. A prioritást egy klasszikus, magyarázható ML-pipeline becsüli szöveges és strukturált jellemzőkből. Három modellt hasonlítottam össze, és nem a legjobb egyetlen aggregált mutatót választottam, hanem azt, amelyik erős P1 recallt, valószínűségi kimenetet és jól védhető magyarázhatóságot ad.
>
> Erre épül a Service Desk Copilot. Mielőtt bármilyen generatív modellhez kerülne adat, a rendszer redaktálja az e-mailt, telefonszámot, azonosítókat és secret-jellegű értékeket, majd közvetlen és közvetett prompt injection jeleket keres. A RAG-réteg verziózott runbookszakaszokat ad stabil evidence ID-val. A promptban külön van a system szabály, a developer feladat és a nem megbízható adat. A kimenet szigorú JSON-sémára validálódik, a kitalált hivatkozásokat a rendszer eltávolítja, a human review és az automation tiltása pedig alkalmazásoldali szabály, ezért az LLM nem írhatja felül. A CI-ben tíz prompt/RAG regressziós eset fut. A projekt őszintén kimondja, hogy a szintetikus eredmény nem termelési bizonyíték; valódi bevezetés előtt anonim adatok, időalapú validáció, shadow mode, monitorozás és rollback kell.

## Ötperces szakmai vonalvezetés

### 1. Miért ezt a problémát választottam?

A saját szakmai hátteremhez szorosan kapcsolódik:

- IT-üzemeltetés és szolgáltatásmenedzsment;
- incident, problem és change folyamatok;
- Microsoft 365, Entra ID, Intune, Windows 365 és Autopilot;
- üzemeltetési biztonság és NIS2-szemlélet;
- automatizáció és felhasználói adoptáció;
- AI/Copilot és prompt használat oktatása 20–30 fős csoportoknak.

Nem egy tőlem idegen mintafeladatot választottam, hanem olyan problémát, amelynek az üzleti és operatív kockázatait is értem.

### 2. Mit építettem?

- reprodukálható szintetikus ticketgenerátort;
- adattisztítási és minőségellenőrzési lépéseket;
- leakage-safe scikit-learn pipeline-t;
- több modell összehasonlítását;
- P1-fókuszú kiválasztási logikát;
- helyi magyarázatot és valószínűségi kimenetet;
- FastAPI-t és Streamlit demót;
- Docker- és CI-folyamatot;
- helyi RAG-runbook tárat;
- PII/secret redakciót;
- közvetlen és közvetett injection-ellenőrzést;
- verziózott promptot, JSON-sémát és hash-alapú auditnyomot;
- offline determinisztikus adaptert és providersemleges LLM interfészt;
- prompt regressziós teszteket;
- threat modelt, LLMOps-tervet, üzleti esetet és interjúanyagot.

### 3. Mi a legfontosabb architekturális döntés?

Az, hogy **az alkalmazás birtokolja a szabályokat, nem az LLM**.

A modell javasolhat szöveget, de nem teheti meg, hogy:

- kikapcsolja a human review-t;
- engedélyezi az automatizálást;
- kitalált hivatkozást tart meg;
- megváltoztatja a promptverziót;
- azt állítja, hogy végrehajtott egy műveletet.

A provider kimenete nem megbízható bemenetként kerül vissza az alkalmazásba, ahol Pydantic-validáció és policy re-enforcement történik.

### 4. Hogyan mértem?

A klasszikus ML-rétegnél:

- accuracy;
- macro F1;
- P1 precision és recall;
- confusion matrix;
- jelölt modellek összehasonlítása;
- holdout értékelés.

A prompt/RAG-rétegnél:

- elvárt runbook retrieval;
- citation count;
- redakció;
- injection detection;
- human review;
- no autonomous execution;
- instruction/data separation;
- strukturált output és promptverzió.

A 10/10 eredmény nem „LLM-intelligencia pontszám”, hanem determinisztikus engineering-invariánsok tesztje.

### 5. Hogyan vinném termelésbe?

1. jóváhagyott, anonimizált valós adatok;
2. label audit és időalapú validáció;
3. probability calibration és költségalapú küszöbök;
4. fix, szakértők által címkézett benchmark;
5. security/privacy/architecture review;
6. shadow mode;
7. analyst assist explicit elfogadással;
8. monitorozás és override-ok elemzése;
9. canary/feature flag;
10. prompt-, modell-, corpus- és alkalmazásrollback.

## Amit nyugodtan állíthatok

- „Én terveztem meg és állítottam össze a teljes referencia-architektúrát.”
- „A repó futtatható és reprodukálható.”
- „A klasszikus ML-réteghez szintetikus adatgenerálás, tréning, modell-összehasonlítás és értékelés tartozik.”
- „A promptot verziózott, sémával és regressziós tesztekkel védett komponensként kezeltem.”
- „A RAG-hivatkozásokat az alkalmazás allowlist alapján ellenőrzi.”
- „A fake provider tesztben szándékosan hibás és szabályt sértő outputot adok, amit az alkalmazás korrigál.”
- „A rendszerben nincs autonóm rendszerbeavatkozási út.”
- „A projekt a saját ITSM/M365/üzemeltetési tapasztalatomra épülő portfólió-megoldás.”
- „Tudom, milyen további kontrollok szükségesek vállalati bevezetéshez.”

## Amit nem állíthatok

- „Ez a modell termelésben 90% fölött teljesít.”
- „Ezt a rendszert egy korábbi munkáltatónál bevezettem.”
- „Az AI automatikusan megoldja az incidenseket.”
- „A prompt injection teljesen kivédhető.”
- „A 10/10 teszt azt jelenti, hogy az LLM mindig helyes.”
- „A runbookok egy konkrét vállalat hivatalos eljárásai.”
- „A szintetikus adat ugyanolyan, mint a valós adat.”
- „Az LLM saját confidence értéke kalibrált valószínűség.”

## Legvalószínűbb technikai kérdések

### Miért klasszikus ML és nem LLM a prioritásra?

A prioritás jól definiált, kis kimeneti terű, költségérzékeny osztályozási feladat. A klasszikus modell gyorsabb, olcsóbb, stabilabb, magyarázhatóbb és natív valószínűséget ad. A generatív modellt ott használom, ahol valóban értéket ad: a visszakeresett információ szintézisénél.

### Miért logistic regression, ha az SVM macro F1-je jobb?

A célfüggvény üzleti. A logistic regression P1 recallja erősebb volt, van `predict_proba`, könnyű confidence gate-et építeni, és a koefficiensek vizsgálhatók. Nem egy leaderboard-cellát optimalizáltam, hanem az operációs modellt.

### Miért 65% a review küszöb?

A portfólióban ez átlátható kezdő policy. Valós környezetben kalibrált valószínűségek, hibaköltség, service/domain bontás és shadow-mode adatok alapján kell meghatározni. A küszöb nem univerzális igazság.

### Miért szintetikus adat?

Mert a valódi ticketadat személyes, biztonsági és infrastruktúra-információkat tartalmazhat. A szintetikus adat nyilvánossá és reprodukálhatóvá teszi a projektet. Cserébe nem állítom, hogy a metrikák valós környezetre általánosíthatók.

### Hogyan kerülöd el a data leakage-et?

A split a preprocessing illesztése előtt történik, és a TF-IDF, one-hot encoder, imputer, scaler, classifier egy pipeline-ban van. Post-decision mezőket nem használok.

### Miért TF-IDF retrieval és nem vector database?

A corpus kicsi, ezért a TF-IDF egyszerű, átlátható, olcsó és teljesen offline reprodukálható. A retriever interfész cserélhető; vector vagy hybrid search akkor indokolt, amikor corpusméret, szemantikai variancia vagy többnyelvűség ezt adatokkal igazolja.

### Hogyan védekezel prompt injection ellen?

Nem egyetlen detektorra támaszkodom. Van normalizálás, direkt jelzésdetektálás, retrieved context scan, instruction/data separation, schema, citation allowlist, no tools, human review és alkalmazásoldali policy. A detektor kockázati jelzés, nem tökéletes pajzs.

### Mi történik, ha az LLM kitalál egy citation ID-t?

A provider output validálása után a citation listát metszi a rendszer a visszakeresett evidence ID-k halmazával. A kitalált ID kiesik. Ettől még a megmaradt hivatkozás relevanciáját külön kell mérni.

### Mi történik, ha az LLM `automation_allowed=true` értéket ad?

Az alkalmazás a validálás után kényszerítetten `false`-ra állítja. Ugyanez történik a mandatory review-val és a promptverzióval. Ez unit teszttel bizonyított.

### Miért van offline determinisztikus adapter?

Hogy API-kulcs és költség nélkül reprodukálható legyen az orchestration, RAG, schema, guardrail és CI. Nem állítom róla, hogy LLM. A külső provider ugyanazon strukturált interfész mögé csatlakoztatható.

### Mit monitoroznál?

Service health, latency, error, fallback, cost; input és redaction/injection arány; retrieval score és no-evidence rate; priority/confidence/override; delayed P1 recall; schema success; citation relevance; unsupported claim; analyst acceptance/edit/reject; drift; biztonsági esemény; adoption és üzleti kimenet.

### Hogyan rollbackelnél?

Külön verzióegység az alkalmazás, ML-model, prompt, schema, runbook corpus, retriever és provider deployment. Feature flaggel vagy korábbi verzióval visszaállítható, miközben a manuális triage folytonossági út marad.

### Mi a legnagyobb gyengeség?

A szintetikus adat és a kicsi, kurált tudásbázis. A projekt engineering-képességet bizonyít, nem termelési teljesítményt. A következő valódi kapu az anonim történeti adat, label audit, temporal split és kontrollált pilot.

### Miben több ez egy ChatGPT-wrappernél?

Van saját ML-réteg, adatpipeline, modellértékelés, RAG, stable evidence ID, PII/secret guardrail, injection kezelés, struktúrált contract, provider output validation, policy enforcement, CI eval, API, UI, Docker, threat model, LLMOps és rollout terv.

### Hogyan skáláznád?

Stateless API, horizontális skálázás, model artifact registry, külön retrieval szolgáltatás, cache, aszinkron feldolgozás, private networking, managed identity, telemetry és queue. A generáció és a UI külön skálázható.

### Hogyan tennéd többnyelvűvé?

Valós többnyelvű benchmark, domainenkénti retrieval mérés, nyelvi normalizálás, multilingual embedding/transformer összehasonlítás, fordítás kockázatának vizsgálata, nyelvenkénti injection és safety tesztek, segmentált metrikák.

### Miért nem finetuning?

Először prompt, retrieval, schema és evaluation segítségével kell tisztázni a hibák okát. Finetuning akkor indokolt, ha elegendő jó minőségű, engedélyezett adat van, és mérhetően javít egy stabil benchmarkon a költség és lifecycle vállalása mellett.

### Miért nem engedsz automatikus remediationt?

Mert a prompt nem jogosultsági rendszer. Valós actionhöz managed identity, allowlist, typed tool, policy-as-code, explicit approval, dry run, audit, rollback, idempotencia és change control kell. Ezt külön fázisban kell bizonyítani.

## Szerepkörönkénti pozicionálás

### AI szakértő / AI transformation

Emeld ki:

- üzleti use case azonosítás és kontrollált priorizálás;
- stakeholder és operating model;
- Responsible AI és governance;
- adoption, feedback és KPI;
- shadow-mode bevezetés;
- IT és üzlet közötti fordítás.

### AI/ML Engineer

Emeld ki:

- adatgenerálás és validáció;
- leakage-safe pipeline;
- modell-összehasonlítás;
- explainability;
- API, teszt, Docker, CI;
- providersemleges integráció;
- monitoring és artifact lineage.

### Prompt Engineer / LLMOps

Emeld ki:

- instruction hierarchy;
- structured output;
- evidence allowlist;
- versioning és hash;
- direct/indirect injection;
- eval cases és release gate;
- output policy re-enforcement;
- failure-driven prompt change.

### Modern Service Manager / M365 Copilot

Emeld ki:

- ITSM-folyamat és major incident gondolkodás;
- M365/Entra/Intune/Windows 365 runbookok;
- human review, ownership, service health;
- adoption és használati metrikák;
- incident/problem/change és release;
- AI mint üzemeltetett szolgáltatás.

### AI Product Manager

Emeld ki:

- user és stakeholder map;
- value hypothesis;
- acceptance criteria;
- build-vs-buy;
- risk-adjusted rollout;
- KPI tree;
- RACI;
- prioritizált roadmap és korlátok.

## STAR-történetek, amelyekhez a projekt kapcsolható

### 1. Üzemeltetési tapasztalatból AI use case

**Situation:** Több környezetben láttam, hogy a ticketek minősége, prioritása és első reakciója eltérő lehet.

**Task:** Olyan portfóliót akartam készíteni, amely nem általános chatbot, hanem mérhető ITSM-problémát old meg.

**Action:** Szétválasztottam a klasszifikációt és a generatív szintézist, majd köré építettem az adat-, safety-, evaluation- és operating kontrollokat.

**Result:** Létrejött egy futtatható, CI-vel védett, interjún kódszinten bemutatható referencia-megoldás.

### 2. Biztonság a látvány helyett

**Situation:** A generatív demók gyakran túl sok autonómiát sugallnak.

**Task:** Bizonyítani akartam, hogy az AI-kimenet nem lehet policy-forrás.

**Action:** No-tool architektúrát, application-owned policy-t, citation filteringet, schema-validációt, injection jelzést és human-review gate-et építettem.

**Result:** A fake provider még szabályt sértő output esetén sem tud automatizálást engedélyezni vagy kitalált hivatkozást megtartani.

### 3. Mérhetőség és őszinte korlátok

**Situation:** Szintetikus projektek hajlamosak túlértékelni a saját pontosságukat.

**Task:** Olyan anyagot akartam, amely szakmai kritikát is kibír.

**Action:** A metrikákat pontosan elválasztottam a termelési állításoktól, és külön dokumentáltam a valós adatos, shadow-mode és monitoring kapukat.

**Result:** A projekt nemcsak eredményt, hanem döntési érettséget és kockázattudatosságot is mutat.

## Zárómondat

> A projekttel azt szeretném megmutatni, hogy az AI-t nem elszigetelt modellként vagy jó hangzású promptként kezelem. A teljes szolgáltatást nézem: üzleti érték, adat, modell, retrieval, prompt, biztonság, emberi döntés, mérés, release, monitorozás és visszaállíthatóság.
