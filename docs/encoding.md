CAISSA FEATURE ENCODING SPEC

1) Board: 8 x 8 = 64 squares

        col0 ...... col7
row7    a8 ........ h8
 .
 .
row0    a1 ........ h1

2) Square index (0-63)
   s = 8r + f (r = row; f = column)

3) Piece type (p)
   pawn 0, knight 1, bishop 2, rook 3, queen 4, king 5

4) colour (k), from the side to move's view
   stm = 0 if white move, 1 if black move
   k = (0 if white else 1) ^ stm
   (side to move pieces are always k = 0)

5) Feature index (0-767)
   s' = s XOR (56 * stm)     flips the board when Black is to move
   i = 12s' + 6k + p
   Scores are from the side to move's view (negate White-view scores when Black is to move).

6) Inverse (from side to move pov)
   s = i // 12
   k = (i % 12) // 6
   p = i % 6

7) Test vectors (white move)
   white pawn a1 -> 0
   white pawn b3 -> 204
   white knight g1 -> 73
   black bishop a4 -> 296
   black king e8 -> 731
   black king h8 -> 767
