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

4) Color (k)
   black 0, white 1

5) Feature index (0-768)
   i = 12s + 6k + p
   side to move: i = 768, on if white move, off if black move
   total: 769

6) Inverse (i-1 because i = 768 is the side to move)
   s = i // 12
   k = (i % 12) // 6
   p = i % 6

7) Test vectors
   black pawn a1 -> 0
   white pawn a1 -> 6
   white pawn b3 -> 210
   white knight g1 -> 79
   black bishop a4 -> 290
   black king e8 -> 725
