const Web3 = require('web3');
const commander = require('commander');
const fs = require('fs');

require('console-stamp')(console, 'HH:MM:ss');

function task(contract, from) {
  setTimeout(function() {
    contract.getPastEvents('Stored', { fromBlock: from, toBlock: 'latest'})
    .then(function(events) {
        if (events.length) {
            for (var i = 0, len = events.length; i < len; i+=1) {
                console.log(events[i]);
                from = events[i].blockNumber
            }
        }
        task(contract, from+1)
    });
  }, 2000);
}

commander
  .version('1.0.0', '-v, --version')
  .usage('[OPTIONS]...')
  .option('-u, --url <url>', 'Connection URL')
  .option('-a, --address <value>', 'Address of the contract')
  .option('-b, --abi <value>', 'Abi of the contract')
  .option('-p, --pk <value>', 'Private key of account to poll')
  .parse(process.argv);

const options = commander.opts();
console.log('URL:', `${options.url}`);
console.log('ADR:', `${options.address}`);
console.log('ABI:', `${options.abi}`);
console.log('PK:', `${options.pk}`);

const json = fs.readFileSync(`${options.abi}`);
const abi = JSON.parse(json);

const web3 = new Web3(`${options.url}`);
const contract = new web3.eth.Contract(abi, `${options.address}`)

console.log('Starting to run the event loop')
task(contract, 0);



