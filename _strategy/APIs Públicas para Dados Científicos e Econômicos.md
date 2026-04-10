# **Arquitetura de Sistemas de Informação Técnica e Científica: Um Guia Exaustivo de APIs Públicas para Pesquisa, Macroeconomia e Engenharia**

A integração de dados em ferramentas especializadas para a comunidade acadêmica e técnica exige uma infraestrutura de dados que seja ao mesmo tempo resiliente, escalável e de fácil acesso. No cenário contemporâneo, a transição para o paradigma de dados abertos (Open Data) tem sido impulsionada por mandatos governamentais e institucionais que reconhecem a informação como um bem público essencial para o progresso científico e econômico.1 Organizações de prestígio global, como a NASA, as Nações Unidas e o Banco Central do Brasil, estabeleceram APIs (Application Programming Interfaces) que funcionam como pontes entre vastos repositórios de conhecimento e sistemas automatizados de descoberta de dados.3  
O desenvolvimento de uma ferramenta que acelere a busca de artigos técnicos e informações bio-médicas, macroeconômicas e de engenharia depende da seleção criteriosa de fontes que ofereçam acesso público, preferencialmente sem a necessidade de chaves de autenticação complexas ou custos de licenciamento.6 Este relatório detalha as principais interfaces de programação disponíveis, explorando sua arquitetura, os mecanismos de recuperação de dados e as implicações de sua utilização para a análise técnica e a indução de cenários econômicos.

## **Infraestrutura de Dados Científicos e Conhecimento Aeroespacial**

A exploração espacial e a observação da Terra geram volumes massivos de dados, estimados em mais de 15 Terabytes por dia apenas pela NASA.1 Para democratizar este conhecimento, a agência opera o portal api.nasa.gov, que atua como um hub centralizado de passagem para diversas APIs desenvolvidas por seus centros de pesquisa.2 A política de acesso da NASA é exemplar: a maioria dos dados é gratuita e acessível via protocolo REST, utilizando o formato JSON para entrega de resultados, o que facilita a integração com linguagens de programação modernas como Python e JavaScript.3  
Para usuários que buscam exploração imediata sem registro, a NASA disponibiliza a DEMO\_KEY, uma chave genérica que permite o acesso inicial a quase todos os recursos, embora com limites de taxa reduzidos.3 O uso intensivo, comum em aplicações de larga escala, requer um registro simples que eleva o limite para 1.000 requisições por hora, garantindo a estabilidade da infraestrutura para toda a comunidade.3

### **Catálogo de APIs Científicas da NASA**

A diversidade das APIs da NASA permite desde o rastreamento de objetos celestes até o monitoramento de desastres naturais em tempo real. A API NeoWs (Near Earth Object Web Service), por exemplo, fornece dados precisos sobre asteroides que se aproximam da Terra, incluindo diâmetros estimados e distâncias de erro, permitindo que pesquisadores construam modelos de risco e trajetórias orbitais.3

| API da NASA | Descrição Técnica e Aplicação | Endpoint Principal / Recurso |
| :---- | :---- | :---- |
| APOD | Astronomy Picture of the Day; metadados e imagens astronômicas diárias para visualização. | https://api.nasa.gov/planetary/apod |
| NeoWs | Near Earth Object Web Service; rastreamento de asteroides e objetos próximos à Terra. | https://api.nasa.gov/neo/rest/v1/feed |
| DONKI | Space Weather Database; notificações sobre clima espacial, CMEs e tempestades geomagnéticas. | https://api.nasa.gov/DONKI/CME |
| EONET | Earth Observatory Natural Event Tracker; monitoramento contínuo de eventos naturais. | https://eonet.gsfc.nasa.gov/api/v2.1/events |
| EPIC | Earth Polychromatic Imaging Camera; imagens de disco completo da Terra em cores naturais. | https://api.nasa.gov/EPIC/api/natural |
| Exoplanet Archive | Acesso a dados de planetas confirmados e candidatos fora do sistema solar. | https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI |

Além do monitoramento espacial, o sistema EONET (Earth Observatory Natural Event Tracker) destaca-se como um protótipo de serviço web que fornece metadados de eventos naturais atualizados continuamente, como furacões e incêndios florestais, servindo como uma base de conhecimento crítica para estudos de geociências e sustentabilidade.1 O acesso a esses dados permite que universidades e centros de pesquisa correlacionem eventos climáticos com outras variáveis socioeconômicas.

## **Governança Global e Estatísticas das Nações Unidas e UNESCO**

O acesso a dados socioeconômicos e educacionais em escala global é facilitado pelas interfaces das Nações Unidas (ONU) e da UNESCO. O portal UNdata é a principal via de acesso programático às estatísticas da ONU, utilizando o padrão SDMX (Statistical Data and Metadata eXchange), que é a infraestrutura de referência adotada por grandes organizações internacionais para garantir a interoperabilidade estatística.4  
A arquitetura do UNdata API é baseada em datamarts que podem ser consultados via REST ou SOAP.11 Cada conjunto de dados (DataFlow) possui uma Definição de Estrutura de Dados (DSD) associada, que descreve as dimensões e codificações utilizadas, permitindo que sistemas automatizados interpretem os dados sem intervenção humana constante.11 Áreas como agricultura, crime, educação, energia e contabilidade nacional são cobertas exaustivamente por este sistema.11

### **Estrutura de Dados e Indicadores Populacionais**

A API de Dados Populacionais da ONU exemplifica o rigor técnico exigido para projeções demográficas. Os usuários podem acessar indicadores específicos para áreas geográficas variadas entre os anos de 1950 e 2030\.13 O sistema de resposta JSON inclui metadados de paginação (pageNumber, pageSize, nextPage), o que é fundamental para ferramentas de análise que processam grandes volumes de registros históricos.13

| Recurso ONU / UNESCO | Tipo de Dado Disponibilizado | Mecanismo de Acesso |
| :---- | :---- | :---- |
| SDG API | Indicadores dos Objetivos de Desenvolvimento Sustentável (ODS) em tempo real. | REST / Swagger |
| Population API | Projeções demográficas, fertilidade e mortalidade global (1950-2030). | REST / JSON |
| UNESCO UIS API | Mais de 4.000 indicadores de educação, ciência, cultura e comunicação. | REST / ODSQL |
| COMTRADE API | Estatísticas detalhadas de comércio internacional de mercadorias. | REST / JSON |
| MBS API | Monthly Bulletin of Statistics; dados econômicos mensais de 200 países. | SOAP / XML |

A UNESCO, através do seu Instituto de Estatística (UIS), fornece acesso a uma base de conhecimento vital para a comunidade docente e universitária. A API do UIS cobre indicadores de educação (SDG 4), ciência, tecnologia e inovação (SDG 9.5), além de estatísticas culturais e de comunicação.14 Embora a API suporte consultas de até 100.000 registros por vez, a organização disponibiliza o Bulk Data Download Service (BDDS) para pesquisadores que necessitam de séries históricas completas em formatos compactados como ZIP contendo arquivos CSV.14

## **Informação Técnica e Engenharia: DevOps, SRE e Cloud Computing**

A busca por conhecimento técnico em Engenharia de Software e infraestrutura é impulsionada por APIs que agregam documentação oficial, cursos e bases de conhecimento comunitárias. Diferente de artigos puramente acadêmicos, estas fontes focam na aplicabilidade prática e na automação, sendo essenciais para o workflow de SRE (Site Reliability Engineering) e DevOps.17  
Para a comunidade docente e acadêmica, o **Microsoft Learn Catalog API** destaca-se por oferecer acesso gratuito e sem autenticação a todo o catálogo de treinamentos, módulos e certificações em Cloud Computing, IA e Engenharia de Software.18 Esta interface permite que instituições de ensino integrem trilhas de aprendizado oficiais em seus próprios sistemas de gestão de aprendizagem (LMS).18

### **APIs de Conhecimento em Engenharia e Infraestrutura**

A automação e a integração através de APIs são pilares do DevOps moderno, permitindo a redução de erros humanos e a aceleração dos ciclos de entrega.

| Provedor Técnico | Especialidade | Endpoint / Recurso Principal | Requisito de Chave |
| :---- | :---- | :---- | :---- |
| Microsoft Learn | Cloud, DevOps, IA, Certificações. | https://learn.microsoft.com/api/catalog/ | Não 18 |
| Stack Exchange | Conhecimento comunitário (DevOps, SRE). | https://api.stackexchange.com/docs | Não (Limitado) 19 |
| GitHub Search | Descoberta de código e padrões DevOps. | https://api.github.com/search/code | Não (Público) 20 |
| Docker Hub | Metadados de containers e infraestrutura. | https://hub.docker.com/v2/repositories/ | Não (Leitura) |
| MDN Web Docs | Padrões Web e Engenharia Frontend. | https://api.github.com/repos/mdn/content | Não |

O **Stack Exchange API** permite consultar as vastas discussões de comunidades como Stack Overflow e DevOps Stack Exchange. Embora permita acesso anônimo, ele impõe limites de paginação (máximo de 25 páginas) e volume diário, recomendando o uso de uma chave de aplicação gratuita para aumentar as quotas para até 10.000 requisições por dia.19

## **Artigos Acadêmicos e Avanços em IA e Data Science**

Para a descoberta de literatura técnica e SOTA (State of the Art) em Inteligência Artificial e Ciência de Dados, o **arXiv API** é a fonte primária de excelência. Ele oferece acesso programático sem chaves a milhões de e-prints em computação e matemática, retornando dados no padrão Atom 1.0.8  
O ecossistema é complementado pelo **Hugging Face Hub API**, que atua como o repositório central para modelos e datasets de IA. Suas APIs permitem filtrar modelos por status de inferência e capacidade de processamento, facilitando a automação de pipelines de Data Science.23

### **APIs de Pesquisa em IA e Biotecnologia**

No setor de biotecnologia e biomédica, as **E-utilities do NCBI (PubMed)** permanecem como o padrão-ouro para a automação de revisões literárias.25 O sistema permite até 3 requisições por segundo sem chave, subindo para 10 rps com um cadastro gratuito.6

| Recurso Científico | Foco | Formato / Interface | Acesso sem Chave |
| :---- | :---- | :---- | :---- |
| arXiv | IA, CS, Física, Matemática. | REST / Atom XML | Sim (Total) 8 |
| Europe PMC | Biomédica e Life Sciences. | REST / JSON | Sim (10 rps) |
| CrossRef | Metadados de DOIs e citações. | REST / JSON | Sim (Polite Pool) |
| OpenAlex | Catálogo global de obras e autores. | REST / JSON | Sim (Limitado) |
| Papers with Code | Benchmarks e links Paper-to-Code. | REST / JSON | Sim (Leitura) 27 |

O **Europe PMC API** oferece uma vantagem técnica significativa sobre o PubMed original: ele permite até 10 requisições por segundo por IP sem qualquer necessidade de registro ou autenticação, fornecendo metadados detalhados de mais de 40 milhões de registros biomédicos.

## **Matrizes Econômicas: Históricos Contábeis e Indutíveis**

Para a construção de matrizes de macroeconomia, o Banco Central do Brasil (BCB) e o IBGE oferecem as fontes primárias mais confiáveis para indicadores brasileiros como IPCA, IGPM e SELIC.5 O Sistema Gerenciador de Séries Temporais (SGS) do BCB é a ferramenta fundamental para consolidar informações econômico-financeiras.5  
A identificação de cada indicador é feita por um código único no SGS. Por exemplo, a URL https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json recupera o histórico completo do IPCA.28

### **Códigos de Séries Temporais para Indicadores Econômicos (BCB SGS)**

A tabela abaixo lista os códigos essenciais para a indução de cenários macroeconômicos e contábeis no Brasil.29

| Indicador Econômico | Código SGS | Frequência de Atualização | Fonte Primária |
| :---- | :---- | :---- | :---- |
| IPCA (Inflação Oficial) | 433 | Mensal | IBGE 29 |
| SELIC (Taxa de Juros) | 11 | Diária | Banco Central 20 |
| IGP-M (Inflação Aluguéis) | 189 | Mensal | FGV 29 |
| Dólar Comercial (Venda) | 1 | Diária | Banco Central 30 |
| INPC | 188 | Mensal | IBGE 29 |
| IPCA-15 (Prévia) | 7478 | Mensal | IBGE 29 |

Para análises regionais e desagregações profundas, o sistema **SIDRA do IBGE** fornece a API de Dados Agregados (v3).31 O SIDRA permite consultas em "cubos", onde se pode filtrar a variação do IPCA por categorias de produtos (alimentação, habitação) em diferentes níveis territoriais.31 O código da tabela 1705 refere-se ao IPCA-15, enquanto a 7060 contém os dados gerais do IPCA.31

## **Ativos Financeiros: Ações, Câmbio e Commodities**

A recuperação de preços históricos de ativos financeiros globais exige interfaces que normalizem dados de diferentes bolsas. Enquanto dados em tempo real são frequentemente pagos, provedores como Alpha Vantage e Finnhub oferecem camadas gratuitas generosas para dados históricos.32

| Ativo Financeiro | Provedor Recomendado | Endpoint / Recurso | Detalhes Técnicos |
| :---- | :---- | :---- | :---- |
| Ações (Global) | Alpha Vantage | /query?function=TIME\_SERIES\_DAILY | Históricos longos em JSON.32 |
| Câmbio (Ptax) | BCB Olinda | /odata/CotacaoDolarDia | Padrão OData oficial. |
| Petróleo (Brent/WTI) | EIA Open Data | /v2/petroleum/prices | Séries diárias oficiais dos EUA.34 |
| Ouro (Spot/Futuro) | B3 / IpeaData | Código SGS: 1650972739 | Históricos via IpeaData.35 |

Para o câmbio oficial no Brasil (PTAX), o Banco Central utiliza a plataforma **Olinda**, que opera com o protocolo OData. Este sistema permite consultas complexas via URL para obter a cotação de venda e compra de moedas estrangeiras para fins contábeis e fiscais.36 No caso do ouro e petróleo, o **IpeaData API** destaca-se como um agregador de séries internacionais (Brent e WTI), facilitando o acesso programático via OData v4.38

## **Conclusões e Recomendações Técnicas**

A construção de uma ferramenta aceleradora de busca baseada em APIs públicas exige uma abordagem de "Design for Resilience". Dado que muitas APIs gratuitas e públicas possuem limites de taxa (rate limits) baseados no endereço IP do usuário, a arquitetura da ferramenta deve priorizar o cache local de dados estáticos.  
As principais recomendações para a implementação incluem:

1. **Abstração de Protocolos:** Desenvolver wrappers que convertam respostas XML (arXiv, PubMed) para JSON, padronizando a saída para a ferramenta de destino.40  
2. **Uso de Metadados de Contexto:** Empregar padrões como AGENTS.md para fornecer aos assistentes de IA instruções claras sobre como navegar nessas documentações técnicas de forma eficiente.41  
3. **Identificação de Séries:** Manter um dicionário interno mapeando os códigos SGS (BCB) e IDs de indicadores da UNESCO para evitar inconsistências em séries históricas.29

O ecossistema de dados abertos técnico-científicos fornece o substrato necessário para uma ferramenta de pesquisa de classe mundial. A integração estratégica das fontes da NASA, Microsoft, arXiv e órgãos financeiros brasileiros permitirá uma aceleração significativa na descoberta de conhecimento e na indução de cenários técnicos.

---

### **Módulo Cultural / Entretenimento / Artes**

Visando expandir as capacidades do Cíbrido para a análise de mídias, indústrias criativas e cultura pop, mapeamos bases de dados massivas de entretenimento com foco em uso acadêmico e de IA:

*   **TMDb (The Movie Database) API**: Avaliada como a base livre mais robusta para catalogação de metadados, elencos, orçamentos, bilheterias e *ratings* de filmes e séries globais. Opera perfeitamente em modo Free/Developer para indexação.
*   **IGDB API (by Twitch/Amazon)**: A base definitiva sobre jogos eletrônicos. Permite extrair esquemas relacionais sobre consoles, franquias, popularidade e agregadores de *reviews* cruzando múltiplas plataformas analíticas.
*   **MusicBrainz API**: Uma enciclopédia musical pura (open-source), indispensável caso a IA precise de dados concretos e validados sobre rótulos, compositores, e estruturação profunda de discografias, sem as amarras comerciais de APIs pagas (como Spotify, que é restrito).
*   **The Met / Cleveland Museum (Arte Visual Clássica)**: Endpoints com licenciamento público de acervos históricos (Open Access) e descrições acadêmicas sobre pinturas, peças arqueológicas e seus autores.
*   **Wikipedia & Wikimedia REST API (Conhecimento Geral/Enciclopédico)**: Escudo definitivo para recuperação em texto limpo de fatos, biografias, eventos geográficos/históricos e resumos rápidos (*Abstracts*). Supre as lacunas deixadas por bases estritamente acadêmicas ou fatias puramente de entretenimento, lidando de forma nativa e sem necessidade de tokens de autenticação (exige apenas respeito aos limites via *User-Agent* nominal ativo).

A integração deste *Pillar Cultural* permitirá relatórios interativos sobre Economia Criativa, cruzando receitas de bilheteria e avaliações artísticas.


#### **Referências citadas**

1. How To Use NASA APIs \- GitHub Pages, acessado em abril 10, 2026, [https://wilsjame.github.io/how-to-nasa/](https://wilsjame.github.io/how-to-nasa/)  
2. nasa/api-docs: api.nasa.gov \- GitHub, acessado em abril 10, 2026, [https://github.com/nasa/api-docs](https://github.com/nasa/api-docs)  
3. NASA Open APIs, acessado em abril 10, 2026, [https://api.nasa.gov/](https://api.nasa.gov/)  
4. UNSD API Catalogue \- the United Nations, acessado em abril 10, 2026, [https://unstats.un.org/unsd/api/](https://unstats.un.org/unsd/api/)  
5. Sistema Gerenciador de Séries Temporais (SGS) \- Banco Central do Brasil, acessado em abril 10, 2026, [https://www4.bcb.gov.br/pec/series/port/aviso.asp?frame=1](https://www4.bcb.gov.br/pec/series/port/aviso.asp?frame=1)  
6. What is an API Key and how can I get it? \- NLM Support Center \- NIH, acessado em abril 10, 2026, [https://support.nlm.nih.gov/kbArticle/?pn=KA-05317](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)  
7. New API Keys for the E-utilities \- NCBI Insights \- NIH, acessado em abril 10, 2026, [https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)  
8. arXiv API Basics, acessado em abril 10, 2026, [https://info.arxiv.org/help/api/basics.html](https://info.arxiv.org/help/api/basics.html)  
9. Fun with NASA's Open Data Portal \- News \- SparkFun Electronics, acessado em abril 10, 2026, [https://news.sparkfun.com/2807](https://news.sparkfun.com/2807)  
10. API Keys and Authentication \- ToolUniverse Documentation \- Zitnik Lab, acessado em abril 10, 2026, [https://zitniklab.hms.harvard.edu/ToolUniverse/guide/api\_keys.html](https://zitniklab.hms.harvard.edu/ToolUniverse/guide/api_keys.html)  
11. api manual \- UNdata, acessado em abril 10, 2026, [http://data.un.org/Host.aspx?Content=API](http://data.un.org/Host.aspx?Content=API)  
12. faq \- UNdata, acessado em abril 10, 2026, [https://data.un.org/Host.aspx?Content=FAQ](https://data.un.org/Host.aspx?Content=FAQ)  
13. Data API \- Data Portal \- the United Nations, acessado em abril 10, 2026, [https://population.un.org/dataportal/about/dataapi)](https://population.un.org/dataportal/about/dataapi\))  
14. Access the UNESCO Institute for Statistics API • uisapi, acessado em abril 10, 2026, [https://tidy-intelligence.github.io/r-uisapi/](https://tidy-intelligence.github.io/r-uisapi/)  
15. API trainings | Institute for Statistics (UIS), acessado em abril 10, 2026, [https://www.uis.unesco.org/en/data-governance/meetings/api-trainings](https://www.uis.unesco.org/en/data-governance/meetings/api-trainings)  
16. uisapi: Access the UNESCO Institute for Statistics API \- CRAN, acessado em abril 10, 2026, [https://cran.r-project.org/package=uisapi](https://cran.r-project.org/package=uisapi)  
17. API:-Introduction to APIs in DevOps/SRE Profile | by Rajkumar Singh | Medium, acessado em abril 10, 2026, [https://medium.com/@rajkumarsingh07/introduction-to-apis-in-devops-sre-a-comprehensive-guide-bc0a53b578cd](https://medium.com/@rajkumarsingh07/introduction-to-apis-in-devops-sre-a-comprehensive-guide-bc0a53b578cd)  
18. Microsoft Learn Catalog API feature overview, acessado em abril 10, 2026, [https://learn.microsoft.com/en-us/training/support/catalog-api](https://learn.microsoft.com/en-us/training/support/catalog-api)  
19. Stack Exchange API v2.3, acessado em abril 10, 2026, [https://api.stackexchange.com/docs](https://api.stackexchange.com/docs)  
20. Taxa de juros \- Selic \- json\_serie-sgs-11 \- Dados Abertos – BCB \- Banco Central do Brasil, acessado em abril 10, 2026, [https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic/resource/b73edc07-bbac-430c-a2cb-b1639e605fa8](https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic/resource/b73edc07-bbac-430c-a2cb-b1639e605fa8)  
21. REST API endpoints for meta data \- GitHub Docs, acessado em abril 10, 2026, [https://docs.github.com/en/rest/meta/meta](https://docs.github.com/en/rest/meta/meta)  
22. arXiv API User's Manual, acessado em abril 10, 2026, [https://info.arxiv.org/help/api/user-manual.html](https://info.arxiv.org/help/api/user-manual.html)  
23. Hub API \- Hugging Face, acessado em abril 10, 2026, [https://huggingface.co/docs/inference-providers/hub-api](https://huggingface.co/docs/inference-providers/hub-api)  
24. Hub API Endpoints \- Hugging Face, acessado em abril 10, 2026, [https://huggingface.co/docs/hub/api](https://huggingface.co/docs/hub/api)  
25. How to Access NCBI Data in Bulk \- NLM Support Center \- NIH, acessado em abril 10, 2026, [https://support.nlm.nih.gov/kbArticle/?pn=KA-05510](https://support.nlm.nih.gov/kbArticle/?pn=KA-05510)  
26. A General Introduction to the E-utilities \- Entrez® Programming Utilities Help \- NCBI \- NIH, acessado em abril 10, 2026, [https://www.ncbi.nlm.nih.gov/books/NBK25497/](https://www.ncbi.nlm.nih.gov/books/NBK25497/)  
27. API Client for paperswithcode.com \- GitHub, acessado em abril 10, 2026, [https://github.com/paperswithcode/paperswithcode-client](https://github.com/paperswithcode/paperswithcode-client)  
28. Índice de Preços ao Consumidor-Amplo (IPCA) \- Serviços \- json\_serie-sgs-10844, acessado em abril 10, 2026, [https://dadosabertos.bcb.gov.br/dataset/10844-indice-de-precos-ao-consumidor-amplo-ipca---servicos/resource/c0980df7-ad92-47af-b71c-790825f4710a](https://dadosabertos.bcb.gov.br/dataset/10844-indice-de-precos-ao-consumidor-amplo-ipca---servicos/resource/c0980df7-ad92-47af-b71c-790825f4710a)  
29. Indicadores Econômicos Consolidados – Tabelas que foram descontinuadas, acessado em abril 10, 2026, [https://www.bcb.gov.br/estatisticas/indecoreestruturacao](https://www.bcb.gov.br/estatisticas/indecoreestruturacao)  
30. Como pegar dados do BANCO CENTRAL com o Python (SELIC, IPCA, IGP-M, USD), acessado em abril 10, 2026, [https://www.youtube.com/watch?v=KKMNdqfzsTI](https://www.youtube.com/watch?v=KKMNdqfzsTI)  
31. Understanding the IBGE Aggregate Data API • ibger, acessado em abril 10, 2026, [https://monitoramento.sepe.pe.gov.br/ibger/articles/api-concepts.html](https://monitoramento.sepe.pe.gov.br/ibger/articles/api-concepts.html)  
32. Alpha Vantage: Free Stock APIs in JSON & Excel, acessado em abril 10, 2026, [https://www.alphavantage.co/](https://www.alphavantage.co/)  
33. Finnhub Stock APIs \- Real-time stock prices, Company fundamentals, Estimates, and Alternative data., acessado em abril 10, 2026, [https://finnhub.io/](https://finnhub.io/)  
34. EIA's API Technical Documentation \- U.S. Energy Information ..., acessado em abril 10, 2026, [https://www.eia.gov/opendata/documentation.php](https://www.eia.gov/opendata/documentation.php)  
35. Ipeadata, acessado em abril 10, 2026, [http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m\&serid=1650972739\&oper=view](http://www.ipeadata.gov.br/ExibeSerie.aspx?module=m&serid=1650972739&oper=view)  
36. Dólar comercial (venda e compra) \- cotações diárias \- API \- Endpoint OData \- Portal de Dados Abertos do Banco Central do Brasil, acessado em abril 10, 2026, [https://dadosabertos.bcb.gov.br/it/dataset/dolar-americano-usd-todos-os-boletins-diarios/resource/061ad7c7-0228-4c33-92ff-b6b3aa0235d2](https://dadosabertos.bcb.gov.br/it/dataset/dolar-americano-usd-todos-os-boletins-diarios/resource/061ad7c7-0228-4c33-92ff-b6b3aa0235d2)  
37. Dólar comercial (venda e compra) \- cotações diárias \- API \- Navegador de Dados, acessado em abril 10, 2026, [https://dadosabertos.bcb.gov.br/dataset/dolar-americano-usd-todos-os-boletins-diarios/resource/ae69aa94-4194-45a6-8bae-12904af7e176](https://dadosabertos.bcb.gov.br/dataset/dolar-americano-usd-todos-os-boletins-diarios/resource/ae69aa94-4194-45a6-8bae-12904af7e176)  
38. FOB \- Ipeadata, acessado em abril 10, 2026, [http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=1650971490](http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=1650971490)  
39. Serviço de consulta aos dados do Ipeadata, acessado em abril 10, 2026, [http://www.ipeadata.gov.br/api/](http://www.ipeadata.gov.br/api/)  
40. parsing, acessado em abril 10, 2026, [https://info.arxiv.org/help/api/examples/perl\_arXiv\_parsing\_example.txt](https://info.arxiv.org/help/api/examples/perl_arXiv_parsing_example.txt)  
41. Announcing General Availability of AWS DevOps Agent | AWS Cloud Operations Blog, acessado em abril 10, 2026, [https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/](https://aws.amazon.com/blogs/mt/announcing-general-availability-of-aws-devops-agent/)  
42. Trending Papers \- Hugging Face, acessado em abril 10, 2026, [https://paperswithcode.com/api/v1/docs/](https://paperswithcode.com/api/v1/docs/)