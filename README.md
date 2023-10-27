Este é o repositório de informação da Iniciação Científica de Gabriel Monteiro.

O sistema (*hardware* e *software*) que está em construção mede tensões com vários sensores e registra essas tensões em arquivos texto.

Um multímetro de precisão também é usado como sensor. Suas medidas serão usadas como referência para avaliação da qualidade dos outros sensores.

Relés são usados para conectar e desconectar as fontes de tensão.

Estes relés e alguns dos sensores são controlados por uma *placa* microcontrolada Arduino Mega que se comunica com um *computador*. No caso é usado um Raspberry Pi modelo 4B com 4Gbytes de RAM com sistema operacional Raspbian. 

Tanto o multímetro quanto a *placa* comunicam-se com o *computador* por portas USB.

Há muitas maneiras de programar a *placa* e o computador de maneira que se comuniquem, por exemplo, executando na *placa* um programa específico a esta aplicação, por exemplo, escrito em linguagem C e compilado com a IDE do Arduino; e executando no computador, por exemplo, um programa de comunicação serial genérico como puTTY ou minicom e alguns *scripts* de sistema operacional.

Esta solução, embora funcional, dificultaria:
	
- reconfigurações no sistema, por exemplo, agregar outros sensores, pois criaria vários programas que precisariam ser ajustados; 
- criação de uma interface gráfica local ao sistema, pois não provê facilidades para criação dessas interfaces;

(Por outro lado, permitiria usar o Raspberry Pi sem gerenciador de interface, o que possibilitaria usar um *computador* com menos capacidade de processamento.)

Optou-se por executar na *placa* um programa de controle genérico e centralizar o desenvolvimento do *software* no *computador*. Desta forma, se conveniente, a leitura do multímetro e dos sensores, o controle dos relés, o gerenciamento dos dados e a interface gráfica podem ser feitos através de um ou mais programas escritos na linguagem Python.

Segue o detalhamento das partes do sistema

- [Detalhamento do *hardware*](hardware.md);
- [Detalhamento do *software*](software.md);




