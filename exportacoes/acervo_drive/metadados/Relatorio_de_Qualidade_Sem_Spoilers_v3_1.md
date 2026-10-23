# Leis para Matar Deuses — edição digital imersiva v3.1

**Autor:** Werik Martins. **Data:** 23/10/2026. **Destino:** leitura digital.

## Entregas

| Arquivo | Conteúdo |
|---|---|
| Leis_para_Matar_Deuses_Vol1_Edicao_Imersiva_v3_1.pdf | Romance integral, 574 páginas; preserva a composição ilustrada v3 e acrescenta 20 páginas de armorial. |
| Leis_para_Matar_Deuses_Vol1_Edicao_Imersiva_v3_1.epub | Texto refluível, imagens, navegação e armorial adaptado para telas menores. |
| Caderno_de_Arte_Imersivo_v3_1.pdf | 113 páginas; preserva as 93 páginas anteriores e acrescenta o armorial. |
| Armorial_de_Aresta_v3_1.pdf | As 20 páginas do novo armorial, também disponíveis separadamente. |
| Armorial_Ativos_Editaveis_v3_1.zip | SVGs e PNGs individuais, originais do GitHub e galeria HTML local. |
| Composicao_Digital_Editavel_v3_1.zip | Capas e mapas em SVG, versões digitais das capas, identidade anterior, medalhões, fontes e licenças. |
| Artes_Nativas_Adicionais_v3.zip | 12 pinturas/composições nativas da etapa v3 e a referência visual atual de Mara; 13 PNGs separados. |

Os pacotes de artes anteriores continuam na pasta da edição v2. A edição v3 foi preservada, assim como seus arquivos de continuação. Os novos arquivos têm nomes v3.1 para evitar substituição acidental.

## Uso do acervo

O repositório `werikvinicios-dev/LTKG` foi consultado somente para leitura. O estado mais recente conferido continua sendo o commit `a15dae77c5f564f4b5d137baf9ee07d490ee1868`. Não houve alterações no GitHub.

Foram conferidos por hash Git os **175 SVGs originais** de cinco famílias: sete leis, seis disciplinas, seis elementos da operação transpositiva, nove entradas de instituições/personagens e sete estudos regionais. Os originais foram preservados no pacote.

O armorial utiliza essas 35 entradas visuais. Para as 16 entradas institucionais e regionais, foram criadas **48 aplicações novas**: 16 brasões, 16 bandeiras e 16 estandartes. Com os emblemas isolados e os símbolos da magia, são 83 arquivos derivados em SVG e 83 exportações PNG. As variantes não são contabilizadas como 83 ilustrações narrativas novas.

As peças novas são propostas editoriais baseadas nos emblemas existentes. Não criam facções, patentes, poderes ou acontecimentos. Os estudos regionais conservam a identificação conceitual do acervo, sem fixar fronteiras, rotas ou distâncias. As famílias de medalhões didáticos v3 e de emblemas originais do repositório permanecem identificadas como tratamentos gráficos distintos.

As pranchas de heráldica, estandartes, objetos, cenários e retratos já presentes na edição v3 foram preservadas. Versões antigas de personagens incompatíveis com as decisões mais recentes não foram reinseridas. Materiais antigos da magia não se sobrepõem à revisão com selos.

## Verificações executadas

- **Integridade do romance:** 31 capítulos do EPUB comparados byte a byte com a versão v3; nenhuma alteração. O corpo narrativo possui 711.764 caracteres após normalização e remoção dos espaços, com SHA-256 `a25ad2943b575cc28bc3bd8ffadf61e0baadbdcb014ee6dcd2522478263bb898`.
- **Integridade do PDF:** todas as páginas anteriores mantêm o mesmo texto extraído; a única exceção intencional é a página de sumário que ganhou o link para o armorial. As 93 páginas anteriores do caderno permanecem intactas.
- **Navegação:** 103 marcadores e 494 links no romance PDF. O armorial possui entrada no sumário e marcadores próprios.
- **EPUBCheck 5.4.0:** zero erros fatais, zero erros e zero avisos na versão final.
- **Tela pequena:** seis páginas representativas do novo armorial conferidas em navegador com largura de 390 px; nenhuma imagem ausente e nenhuma rolagem horizontal. Conferência adicional em largura de 1.000 px.
- **Revisão visual:** todas as 20 páginas novas revisadas em prancha de contato; páginas representativas também em tamanho maior. Legendas do EPUB tiveram contraste corrigido. Nenhum texto novo ultrapassa a área segura do PDF.
- **Geometria dos símbolos:** as cópias de aplicação receberam área de desenho suficiente para preservar traços que ultrapassavam o enquadramento de alguns SVGs originais. Os originais continuam inalterados.
- **Imagens:** PNGs das novas peças heráldicas foram renderizados diretamente de vetores. Não foram ampliados bitmaps pequenos para simular qualidade de impressão.

## Pendências e limites reais

A edição é digital. Não é um arquivo certificado para impressão nem possui especificação de lombada ou perfil de gráfica. O EPUB foi validado tecnicamente e em navegador; não foi testado fisicamente em todos os modelos de Kindle, Kobo ou Apple Books.

A referência visual atual de Mara e uma descrição antiga ainda presente no manuscrito divergem. A mudança visual foi respeitada no atlas, e o texto narrativo foi preservado. A divergência já registrada continua pendente de decisão textual do autor; não foi corrigida silenciosamente por uma alteração gráfica.

Novas paletas e aplicações heráldicas continuam sendo propostas gráficas, não aprovação automática de novo cânone. Os nomes dos estudos regionais pertencem ao acervo conceitual e não substituem a nomenclatura geográfica do romance.

O caderno de arte completo deve ser lido depois do romance para preservar a ordem de descoberta. O percurso visual sem spoilers da edição v3 permanece disponível separadamente.

Os prompts exatos de algumas pinturas v3 não estavam no ponto de recuperação. Os PNGs nativos foram preservados; descrições reconstruídas de produção não serão apresentadas como prompts originais.
