.. pdfinfo::
  :place: Kraków
  :date: 2020-03-28
  :contest_name: Uniwersyteckie Zawody Informatyczne
  :contest_date: Jagiellonian Programming League
  :leftlogo: uzi.pdf
  :rightlogo: tcs.pdf

.. |vspace| raw:: latex

   \vspace{2mm}
   
.. |noindent| raw:: latex

   \noindent

.. |br| raw:: html

   <br />


Problem E: Civilizations
=================================================
|noindent| **Time limit: Xs, memory limit: 512MB.**
|vspace| |br|

There is a new hot game in development: Civilizations (not to be confused with Civilization).
As one of the *Señor Developers* on the team, it is your job to write the main game engine.

The world is divided into :math:`n` rows and :math:`n` columns of unit fields.
The unit field in the :math:`i`-th row and :math:`j`-th column is initially owned by civilization :math:`p_{i,j}` [#]_,
and has value :math:`v_{i,j}`, which corresponds to resources that are present there.

For a given civilisation, we define two important measures: its *wealth* (:math:`w_p`) and *length of borders* (:math:`l_p`).
The wealth of civilisation :math:`p` is the total value of the fields it owns,
while the length of borders is the number of unordered pairs of fields :math:`\{a, b\}`,
such :math:`a` and :math:`b` share a side, and exactly one of them is owned by :math:`p`.

The game engine will have to handle a sequence of events; in each, the owner of one of the fields
changes, as a result of a war between two civilisations. [#]_ After each such event, the engine should
determine how powerful is the current *most powerful civilisation*, out of civilisations that own at **at least one field**.

The game design team has already decided that the *power* of civilisation :math:`p` will be computed as
:math:`A w_p + B l_p + C w_p l_p`. This is where things get tricky though: the definition of power
changes as the situation in the game world develops! After each event, your engine will be supplied with new values
for the coefficients :math:`A`, :math:`B` and :math:`C`.

Of course, your engine also has to be fast -- otherwise *Civilizations* players will get bored!


.. [#] You can assume that for every non-negative integer, there is a civilisation corresponding to that integer. Of course, at any given time only a finite number of them will own some part of the world.
.. [#] The changes from the events persist (i.e. each change affects future events).

Input
-------

The first line of input contains the number of test cases :math:`z` (:math:`1 \leq z \leq 2000`). The descriptions of the test cases follow.

The first line of every test case contains single integer :math:`n` (:math:`2 \leq n \leq 500`) -- the size of the world.

The next :math:`n` lines contain :math:`n` integers each, and describe field values :math:`v_{i,j}` (:math:`|v_{i,j}| \leq 100`).

The next :math:`n` lines contain :math:`n` integers each, and describe field owners :math:`p_{i,j}` (:math:`0 \leq p_{i,j} \leq 10^9`).

The next line consists of a single integer :math:`q` (:math:`1 \leq q \leq 10^5`) -- the number of events.

The next :math:`q` lines describe the events. They contain six integers each :math:`i`, :math:`j`, :math:`p`, :math:`A`, :math:`B`, :math:`C`
(:math:`1 \leq i, j \leq n`; :math:`0 \leq p \leq 10^9`; :math:`|A| \leq 10^{10}`; :math:`|B| \leq 10^{12}`, :math:`|C| \leq 10^4`);
corresponding to: the row and column of the field that changes owners, the new owner civilisation,
and the coefficients to compute the civilisation power, respectively.
It is guaranteed that before the event civilisation :math:`p` did not own the field :math:`(i, j)`.

The total number of unit fields in all test cases does not exceed :math:`500\,000`.

The total number of queries in all test cases does not exceed :math:`200\,000`.

Output
-------

For each test case output a single line containing :math:`q` integers: the power value of the most powerful civilisation after each of the events.

Example
--------

.. list-table::
 :header-rows: 1

 * - For an example input
   - the correct output is
 * - ::

      1
      2
      1 2
      3 4
      1 1
      2 2
      6
      2 2 1 1 -1 0
      1 2 2 1 2 -1
      2 1 6 0 1 -1
      1 2 6 2 0 0
      1 1 6 1 1 1
      2 2 6 -1 -1 -1

   - ::

      5 -7 -2 10 20 -10

Explanation
-----------

After the first event, civilisation 2 owns only the :math:`(2, 1)` field, while civilisation 1 owns the rest.
Both civilisations have borders of length 2, and their wealth is 7 and 3, respectively.
The civilisation 1 with power of 5 is the most powerful.

After the second event, civilisation 1 owns fields on one diagonal, while civilisation 2 on the other.
Both civilisations have borders of length 4, and wealth of 5, so they are equally powerful with power of -7.

After the third event, there are now three civilisations on the board: 1, 2 and 6.
The civilisation 6 is now the most powerful.

Finally, in the last three events, civilisation 6 takes over the remaining fields.
Note that now 6 is the most powerful civilisation for any :math:`A`, :math:`B` and :math:`C`, since we only take into account civilisations controlling at least one field.
The power of civilisation 6 at the end of the game is -10, since it has borders of length 0, and wealth of 10.