Obscuro Test Framework (multiple networks)
------------------------------------------
Project repo for building and running solidity smart contracts on Ethereum against a variety of networks e.g. 
[ganache](https://trufflesuite.com/ganache/), [ropsten via infura](https://infura.io/), 
[geth](https://geth.ethereum.org/docs/getting-started), and  [obscuro](https://obscu.ro/). The repo uses the 
[pysys](https://pysys-test.github.io/pysys-test/) test framework to manage all tests and their execution. All tests are 
fully system level using [web3.py](https://web3py.readthedocs.io/en/stable/) to interact with the networks which are 
managed outside the scope of the tests. Note the project is currently under continuous active development and further 
information on running the tests will be added to this readme over time. 


Repository Structure
--------------------
The top level structure of the project is as below;

```
├── README.md            # Readme 
├── .default.properties  # Default properties file detailing connection and keys required for running 
├── pysysproject.xml     # The pysys project file
├── admin                # Used for administering Obscuro testnet 
├── artifacts            # Artifacts used during test execution (e.g. Obscuro wallet extension)
├── src                  # The project source root for test execution 
│    └── python          # Python source code as extension to pysys for ethereum interaction
├── tests                # The project test root for all tests 
│    ├── generic         # Network agnostic tests 
│    └── obscuro         # Obscuro specific tests 
└── utils                # The project utils root for utilities used by the tests
     ├── contracts       # A library of smart contracts 
     └── docker          # Used to build and run a linux docker container to run the tests 
```

The [.default.properties](./.default.properties) file contains properties for running the tests that are common to any 
user running the tests. User specific properties should be added into a `.username.properties` file at the root of the 
project. As this file could contain sensitive data it should never be committed back into the main repo (the 
[.gitignore](./.gitignore) should prevent this). Properties will first be looked for in a `.username.properties` should
it exist, and if not will fall back to the default properties. 

Setup
-----
The easiest way to set up a host to run the tests is to create a docker container with all dependencies pre-installed. 
The repository should be cloned into the same parent directory as [go-obscuro](https://github.com/obscuronet/go-obscuro)
as running the tests will use the wallet_extension built from the working copy of the go-obscuro repository. To build 
the wallet_extension and the docker container, in the root of the repository run;

```bash
./utils/docker/build_image.sh
```

Once built, to connect to the container run;

```bash
./utils/docker/run_image.sh
```


Running the tests
-----------------
To run the tests against Obscuro testnet, change directory to the `tests` directory and run;

```bash
cd /home/obscuro-test/tests/generic && pysys.py run 
```












