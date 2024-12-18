## Задача 2

### Решение

Было решено парсить файл /proc/\<pid>/maps и строить граф старым добрым dot. Я пошел простым путем и написал скрипт на питоне, подтянув API dot'а через pydot. Запускается срикпт так:

```bash
python3 tabmap.py <path to maps-like file> <graph name>
```

По отношению к реализации есть пара важных замечаний:

1. Обратите внимание, что скрипт я писал под свою систему, в которой файл maps имеет вид, аналогичный sample.dat. Как нетрудно заметить, адреса там 48-битные, что, если я нигде не ошибся, означает отсутствие уровня P4D в иерархии таблиц. Соответственно, выходную картинку следует интерпретировать как PGD->PUD->PMD->PTE->Offset, где оранжевым помечены выделенные участки памяти. Надеюсь, остальные элементы выходной картинки получились достаточно интуитивно понятными. Отдельно замечу, что я использовал рекурсивный подход к построению графического дерева, поэтому смасштабировать его под 64-битные адреса совсем нетрудно.

2. Нетрудно заметить, что при большом количестве выделенных участков близкие стрелки на картинке плохо различимы. Это однако не является большой проблемой, поскольку печать каждого следующего уровня происходит по глобальному порядку, учитывающему и порядок верхних уровней, а значит соотнести узел графа, соответствующий таблице, с ее адресом в вышестоящей таблице можно и вроде бы не очень трудно.

### Отзыв

Отличное задание, очень творческое, с массой вариантов решения. Единственное замечние: кажется, я выбрал вариант решения, слабо связанный собственно с системным программированием. Если при этом не произошло недопонимания и я сделал то, что просили в условии (на что я очень надеюсь, конечно), это значит, что такие варианты решения этой задачи существуют и легитимны. Хорошо это или плохо — решать Вам, мне в любом случае было интересно и весело. Ну и в лишний раз открыть документацию по дереву таблиц пришлось, поэтому совсем уж оторванной от темы курса эту задачу точно назвать нельзя.
