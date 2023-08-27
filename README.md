# layout-genetic-alg
## Motivation
A genetic algorithm utilizing discrete event simulation to help identify optimal layouts for IE 484 project.

We were given a mock factory layout in a simple grid in the ARENA simulation language and told to optimize the layout using the algorithms we learned in class such as CRAFT and MULTIPLE.

I decided overkill was under-rated and rebuilt the entire simulation in SimPy, and created a genetic algorithm to work towards an optimal layout.

![Genetic Alg Snip](https://github.com/LANUMM/layout-genetic-alg/assets/73083827/bba617fd-2c24-4e5d-b929-8965e45b5261)

The scoring was performed by running multiple discrete event simulations for each layout and taking the average objective score over those simulations.
It worked! It was a bit of a rush job so please don't judge it too hard. Since this project I have come to learn the value of TTD, and in future implementations of this project I hope to polish it up, and generalize it to accept a broader problem set. I believe combining the power of discrete event simulation and genetic algorithms is a potentially very powerful tool to help optimize layouts.  

## Setup 
After cloning the repo, you can install dependencies with the following: 
```
pip install -r requirements.txt
```
From there, you can run the project with:
```
python genetic_algorithm.py
```

## More Background
Using python was not originally part of the project scope, and it was all meant to be done in ARENA. That is why the layout csv files are so hard to interpret, they came from ARENA, and the output had to go back into ARENA too, as the score in ARENA is what I was graded on. Here is more background on the project itself:

The given factory scenario involves a five by five grid with a raw storage and end-products storage outside of the system to the left and right of the layout. There are 5 kinds of machines, each which has 5 possible operations it can perform. There are 5 of each machine type, making 25 machines total. 
There are ten different job types which arrive based on an exponential distribution. The different jobs require different sequences of up to five different operations, meaning that some jobs will require every type of machine while others require less.

The objective function (to minimize) is as follows:
```
Objective Function = 2*[Average Customer Waiting Time] + [Average Quantity of Parts In System]
```

origional_map.csv held the original layout given to us.

operation_order.csv describes which job types need to go through what operations and in what order.

ptime.csv describes the processing time for each job at each operation step.

type_prob.csv holds the probabilities of each type of job arriving to the system. 

