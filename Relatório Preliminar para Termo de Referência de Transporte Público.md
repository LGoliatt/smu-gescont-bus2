# Relatório Preliminar para Termo de Referência de Transporte Público

## Introdução

O presente relatório visa consolidar as informações e referências necessárias para a elaboração de um Termo de Referência (TdR) abrangente e moderno para sistemas de transporte público, com foco especial nas tecnologias de bilhetagem digital e biométrica, segurança da informação e conformidade com normativas nacionais e internacionais. A modernização dos sistemas de transporte público é crucial para a melhoria da mobilidade urbana, oferecendo maior eficiência, segurança e comodidade aos usuários, além de otimizar a gestão operacional para as empresas e órgãos gestores. Este documento compila dados de normas técnicas, estudos de caso e melhores práticas do setor, fornecendo um embasamento sólido para a definição dos requisitos técnicos, operacionais e legais que deverão constar no TdR.

A transição para sistemas de bilhetagem eletrônica e a incorporação de tecnologias biométricas representam avanços significativos, mas também impõem desafios relacionados à interoperabilidade, segurança de dados e privacidade dos usuários. Portanto, um TdR bem elaborado é fundamental para garantir que as soluções implementadas sejam robustas, escaláveis e alinhadas com as melhores práticas globais, protegendo os interesses de todas as partes envolvidas e promovendo um serviço de transporte público de alta qualidade.

## Contextualização e Justificativa

A elaboração de um Termo de Referência detalhado é o primeiro passo para a contratação e implementação de soluções tecnológicas eficazes no transporte público. Este documento servirá como guia para fornecedores, especificando os requisitos mínimos, os padrões de desempenho esperados, as normas técnicas a serem seguidas e os critérios de avaliação das propostas. A ausência de um TdR claro e completo pode resultar na aquisição de sistemas inadequados, incompatíveis ou que não atendam às necessidades reais dos usuários e do sistema de transporte como um todo.

As informações compiladas neste relatório, provenientes de fontes como o arquivo fornecido pelo usuário contendo normas técnicas internacionais, o estudo de caso sobre a implantação da bilhetagem eletrônica na Região Metropolitana de Porto Alegre (Lübeck et al., 2012) e o artigo sobre os benefícios da bilhetagem eletrônica no transporte urbano (Praxio, 2023), demonstram a complexidade e a importância de se considerar múltiplos aspectos na modernização dos sistemas de bilhetagem. A seguir, detalharemos os principais componentes que devem ser abordados no TdR.

## Requisitos para Bilhetagem Digital

A bilhetagem digital é a espinha dorsal dos sistemas modernos de arrecadação no transporte público. O TdR deve especificar claramente os requisitos para diferentes tecnologias de bilhetagem digital, garantindo a interoperabilidade e a segurança das transações. As seguintes normas e padrões são fundamentais e devem ser referenciadas:

- **ISO/IEC 14443**: Esta norma define a comunicação sem contato para cartões inteligentes (contactless), amplamente utilizada em cartões de transporte em todo o mundo. O TdR deve exigir conformidade com esta norma para garantir a compatibilidade com uma vasta gama de dispositivos e sistemas.
- **ISO/IEC 7816**: Para sistemas que ainda utilizem ou necessitem de compatibilidade com cartões com contato físico (smartcards), esta norma, que define a estrutura de dados e os comandos, é essencial.
- **ISO/IEC 18092 / NFC Forum Specs**: A Comunicação por Proximidade (NFC) permite transações rápidas e convenientes usando smartphones e outros dispositivos. O TdR deve contemplar a adoção de tecnologias NFC, especificando a conformidade com estas normas para garantir a interoperabilidade e a segurança.
- **EMVCo Contactless Specifications**: Com a crescente convergência entre sistemas de pagamento de transporte e sistemas bancários, a conformidade com as especificações EMV para pagamentos contactless é crucial. Isso permite que os usuários utilizem seus cartões bancários diretamente no sistema de transporte, aumentando a conveniência.
- **Calypso Standard**: Este padrão aberto para bilhetagem eletrônica é amplamente adotado na Europa e América Latina. Considerar a compatibilidade ou a adoção do padrão Calypso pode facilitar a integração com sistemas existentes e futuros, além de promover a concorrência entre fornecedores.

O TdR deve também abordar a utilização de QR Codes como meio de pagamento, especificando os padrões de segurança e formato para sua geração e validação. A capacidade de recarga online, a integração com aplicativos móveis e a disponibilização de informações em tempo real sobre saldos e histórico de transações são funcionalidades que agregam valor ao usuário e devem ser consideradas.

## Requisitos para Bilhetagem Biométrica

A bilhetagem biométrica, utilizando características como reconhecimento facial ou impressão digital, oferece um nível adicional de segurança e personalização, especialmente útil na gestão de gratuidades e benefícios, além de combater fraudes. O TdR deve estabelecer requisitos claros para a implementação de sistemas biométricos, com atenção especial à precisão, velocidade, segurança e privacidade dos dados. As seguintes normas são relevantes:

- **ISO/IEC 19794-5 (Reconhecimento Facial) e ISO/IEC 19794-2 (Impressões Digitais)**: Estas normas especificam os formatos de dados para intercâmbio de informações biométricas faciais e de impressões digitais, respectivamente. A conformidade é essencial para garantir a interoperabilidade entre diferentes sistemas e componentes biométricos.
- **ISO/IEC 30107-3 (Detecção de Apresentação - PAD)**: Para evitar fraudes por meio de falsificações (como fotos ou máscaras no reconhecimento facial, ou moldes de digitais), o TdR deve exigir mecanismos robustos de Detecção de Ataques de Apresentação (PAD), em conformidade com esta norma.
- **ISO/IEC 19785 (CBEFF - Common Biometric Exchange Formats Framework)**: Esta norma define uma estrutura para o intercâmbio de dados biométricos, facilitando a integração de diferentes tecnologias e fornecedores.
- **Padrões como FBI EBTS e ANSI/NIST-ITL 1-2011**: Embora sejam padrões americanos, podem servir como referência para a qualidade e o formato dos dados biométricos, especialmente em contextos que exigem alta precisão e interoperabilidade.

É crucial que o TdR detalhe os requisitos de desempenho para os sistemas biométricos, como taxas de falsa aceitação (FAR) e falsa rejeição (FRR), tempo de processamento e capacidade de funcionamento em diferentes condições ambientais (iluminação, etc.). A privacidade dos dados biométricos é uma preocupação primordial, e o TdR deve remeter às normas de segurança e proteção de dados discutidas a seguir.

## Segurança da Informação e Privacidade de Dados

A coleta, o processamento e o armazenamento de dados de bilhetagem, especialmente dados biométricos e informações pessoais dos usuários, exigem um framework de segurança da informação robusto e em conformidade com as legislações de proteção de dados. O TdR deve ser rigoroso ao especificar os requisitos de segurança:

- **ISO/IEC 27001**: Esta é a principal norma internacional para sistemas de gestão da segurança da informação (SGSI). O TdR deve exigir que os fornecedores demonstrem conformidade com a ISO/IEC 27001, ou que possuam certificação, para garantir que as melhores práticas de segurança sejam implementadas em todos os processos e sistemas.
- **ISO/IEC 24745**: Esta norma fornece diretrizes específicas para a proteção de informações biométricas, incluindo aspectos de privacidade e segurança. Sua observância é fundamental em sistemas que utilizam biometria.
- **GDPR (Regulamento Geral sobre a Proteção de Dados da União Europeia) e LGPD (Lei Geral de Proteção de Dados Pessoais do Brasil)**: O TdR deve exigir total conformidade com a legislação de proteção de dados aplicável. Isso inclui princípios como minimização da coleta de dados, consentimento informado, transparência no uso dos dados, direito de acesso e exclusão pelos titulares, e a implementação de medidas técnicas e organizacionais para proteger os dados contra acesso não autorizado, perda ou destruição.

O TdR deve detalhar requisitos específicos como criptografia de dados em trânsito e em repouso, controle de acesso baseado em função (RBAC), trilhas de auditoria completas e seguras, planos de resposta a incidentes de segurança e avaliações periódicas de vulnerabilidade e testes de penetração.

## Integração, Interoperabilidade e Escalabilidade

Um sistema de transporte público moderno não opera isoladamente. O TdR deve enfatizar a necessidade de integração com outros sistemas (como planejamento de rotas, gestão de frotas, sistemas de informação ao usuário) e a interoperabilidade entre diferentes modais de transporte e, potencialmente, com sistemas de outras cidades ou regiões. A arquitetura da solução deve ser baseada em padrões abertos e APIs bem documentadas para facilitar futuras integrações e evitar a dependência de um único fornecedor (vendor lock-in).

A escalabilidade do sistema é outro requisito crucial. O TdR deve especificar a capacidade atual e futura esperada em termos de número de usuários, transações por segundo, volume de dados armazenados, etc., garantindo que a solução possa crescer de acordo com a demanda sem degradação do desempenho.

## Considerações Adicionais do Estudo de Caso de Porto Alegre e Melhores Práticas

O estudo de caso da implantação da bilhetagem eletrônica na Região Metropolitana de Porto Alegre (Lübeck et al., 2012) destaca que a inovação no transporte público, impulsionada pela bilhetagem eletrônica, vai além da simples adoção tecnológica. Os efeitos da bilhetagem, como a melhoria na gestão das informações, o controle mais preciso das operações e a qualificação do serviço, são os verdadeiros indicadores de inovação. O estudo ressalta a importância da formação de consórcios gestores e a necessidade de adaptação às demandas dos usuários e do poder concedente. Esses aprendizados devem informar o TdR, incentivando modelos de governança colaborativa e a flexibilidade para evoluções futuras.

O artigo da Praxio (2023) reforça os múltiplos benefícios da bilhetagem eletrônica, como a criação de redes integradas, maior segurança para passageiros e operadores (redução de dinheiro em espécie nos veículos), integridade e transparência no uso de benefícios, melhor planejamento da oferta de serviços com base em dados, redução do tempo de embarque e economia de custos operacionais. O TdR deve buscar maximizar esses benefícios, especificando funcionalidades que os suportem, como a geração de relatórios gerenciais detalhados e a capacidade de integração com sistemas de Business Intelligence (BI).

## Conclusão Preliminar

A elaboração de um Termo de Referência robusto e detalhado é um passo crítico para o sucesso na modernização dos sistemas de transporte público. Ao incorporar as normas técnicas internacionais, as lições aprendidas em implementações anteriores e as melhores práticas do setor, o TdR pode guiar a seleção e implementação de soluções de bilhetagem digital e biométrica que sejam seguras, eficientes, interoperáveis e centradas no usuário. Este relatório preliminar fornece a base de informações para a construção desse TdR, que deverá ser continuamente refinado e validado pelas partes interessadas.

## Referências

- Lübeck, R. M., Wittmann, M. L., Battistella, L. F., & da Silva, M. S. (2012). INOVAÇÃO NO TRANSPORTE PÚBLICO: A IMPLANTAÇÃO DA BILHETAGEM ELETRÔNICA NA REGIÃO METROPOLITANA DE PORTO ALEGRE. *Gestão & Regionalidade*, 28(82), 35-47. (Fonte: /home/ubuntu/references/estudo_caso_porto_alegre.txt)
- Praxio. (2023). *Bilhetagem eletrônica: o que é e benefícios no transporte urbano*. Blog da Praxio. (Fonte: /home/ubuntu/references/praxio_blog_bilhetagem.md)
- Normas Técnicas Internacionais para Bilhetagem Digital e Biométrica. (Fonte: Arquivo fornecido pelo usuário, compilado em /home/ubuntu/references/compilacao_referencias.md)

