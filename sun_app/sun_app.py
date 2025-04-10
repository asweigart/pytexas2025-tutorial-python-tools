import examplesky

if examplesky.__version__ != '4.0':
    raise Exception('The sun app requires version 4.0 of examplesky!')

print(r"""
                        |
                    .   |
                        |
          \    *        |     *    .  /
            \        *  |  .        /
         .    \     ___---___     /    .  
                \.--         --./     
     ~-_    *  ./               \.   *   _-~
        ~-_   /                   \   _-~     *
   *       ~-/                     \-~        
     .      |                       |      .
         * |                         | *     
-----------|                         |-----------
  .        |                         |        .    
        *   |                       | *
           _-\                     /-_    *
     .  _-~ . \                   /   ~-_     
     _-~       `\               /'*      ~-_  
    ~           /`--___   ___--'\           ~
           *  /        ---     .  \   jgs
            /     *     |           \
          /             |   *         \
                     .  |        .
                        |
                        |
""")