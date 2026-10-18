CAISSA FEATURE ENCODING SPEC

1) Board: 8 x 8 = 64 squares

        col0 ...... col7
row7    a8 ........ h8
 .
 .
row0    a1 ........ h1

2) Square index (0-63)
   s = 8r + f        r = row (0 = rank 1, White's side), f = column (0 = file a)

3) Piece type (p)
   pawn 0, knight 1, bishop 2, rook 3, queen 4, king 5

4) Colour (k)
   white 0, black 1

5) Feature index (0-767)
   i = 12s + 6k + p
   768 = 64 squares x 2 colours x 6 piece types

6) Inverse
   s = i // 12
   k = (i % 12) // 6
   p = i % 6

7) Test vectors
   white pawn   a1 -> 0   (minimum)
   white pawn   b3 -> 204
   white knight g1 -> 73
   black bishop a4 -> 296
   black king   e8 -> 731
   black king   h8 -> 767 (maximum)

8) Not encoded
   side to move, castling rights, en passant