# layout-genetic-alg
A genetic algorithm to help identify optimal layouts for IE 484 project.

We were given a mock factory layout in a simple grid in the ARENA simulation language and told to optimize the layout using the algorithms we learned in class such as CRAFT and MULTIPLE.

I decided overkill was under-rated and rebuilt the entire simulation in SimPy, and created a genetic algorithm to work towards an optimal layout.

![Genetic Alg Snip](https://github.com/LANUMM/layout-genetic-alg/assets/73083827/bba617fd-2c24-4e5d-b929-8965e45b5261)

The scoring was performed by running multiple discrete event simulations with the layout and taking the average objective score.
It worked! It was a bit of a rush job so please don't judge it too hard. Since this project I have come to learn the value of TTD, and in future implementations of this project I hope to polish it up, and generalize it to accept a broader problem set. 
