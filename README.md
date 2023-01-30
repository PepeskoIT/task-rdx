# Introduction

The challenge has three parts:
* Infrastructure: requires running a fullnode and a network Gateway.
* Coding challenge that will use the infrastructure setup in the first place
* Questions about the Radix network

## Full Node and Core API

When third parties want to integrate the Radix Network (e.g. adding XRD to an exchange), they need to install a full node to use as an endpoint to get a full, reliable stream of all transactions on the Radix network via the Core API that the full node offers. Here are the key parts of the Radix Tech Docs that include instructions on how to install a full node.

* [The Core API](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/radixdlt/radixdlt/1.1.1/radixdlt-core/radixdlt/src/main/java/com/radixdlt/api/core/api.yaml#section/Overview)
* [Full Node Introduction](https://docs.radixdlt.com/main/node-and-gateway/node-introduction.html)
* [Full Node Setup](https://docs.radixdlt.com/main/node-and-gateway/node-setup-introduction.html)
  * [CLI method](https://docs.radixdlt.com/main/node-and-gateway/cli-install.html)
  * [Docker method](https://docs.radixdlt.com/main/node-and-gateway/docker-install-node.html)

Once your full node is installed, you can then use the RadixNode CLI to configure your full node to expose the Core API. A complete list of commands within the RadixNode CLI can be found on GitHub [here](https://github.com/radixdlt/node-runner#interaction-with-node). We recommend that you only expose the Core API privately. It should never be exposed publicly.

The Core API provides a transaction stream (indexed, and strictly ordered) that can be used to synchronize a full or partial view of the ledger, transaction by transaction. Using Core API, you may observe deposits and withdrawals across all accounts (called Data API), as well as build transactions (called Construction API). You can then parse that data in any way that you think is useful for your project. By Radix’s consensus design, transactions have deterministic finality and so all transactions that appear via the Core API are ordered, truly final and cannot be reversed; no “number of blocks” threshold of safety is needed.

To monitor the health of your node, we recommend you use Prometheus and Grafana with the RadixNode CLI.
* [Setting up the Grafana dashboard using the RadixNode CLI](https://docs.radixdlt.com/main/node-and-gateway/install-grafana-dashboard.html)

## Network Gateway and Gateway API
As per above, the Core API provides low-level transaction-by-transaction data. Some exchanges and other service providers prefer a higher-level API for making specific queries on transactions or addresses, and a simplified method of creating and submitting transactions. Typically, this would be in addition to the Core API – not as a replacement for it. This is why we have created the Network Gateway and Gateway API, which is also used by the Radix Desktop Wallet and Explorer.

The Network Gateway is software that you can install. Like the full node, you should run a Network Gateway for your own consumption if you desire to use the Gateway API. The Network Gateway is designed to take the Core API transaction stream from your node, add it to a PostgreSQL database (via the Data Aggregator), and then present the Gateway API for public consumption. Transactions can also be submitted via Gateway API, for example from wallets.
* [An Introduction to the Network Gateway](https://docs.radixdlt.com/main/node-and-gateway/network-gateway.html)
* [The Gateway API](https://docs.radixdlt.com/main/apis/gateway-api.html)
* [Radix Gateway API (1.1.2)](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/radixdlt/radixdlt-network-gateway/1.1.1/gateway-api-spec.yaml)

# Infrastructure Challenge

Following the instructions and links described in the introduction, you need to achieve the following:
* Install a fullnode connected to mainnet and network gateway
* Configure monitoring using the node cli  (or any other method)

You can install this in a personal machine or in any cloud provider of your choice. Before the interview:
* Commit to the repository the docker-compose file that you use to deploy the fullnode, network gateway and Grafana
* Provide a screenshot of the Grafana dashboard
* Brief summary of the challenges

**During the interview you’ll have to share your screen showing the setup**


# Coding challenge

Using the Core API, design and implement a system that is continuously pulling all the submitted transactions to the network and detects a token transfer of any type. 

* When a transfer is detected, store information regarding the token transferred and the total amount transferred. 
* Given a list of account addresses, just store transfers involving (sending or receiving) those accounts and discard the rest.
* Data can be stored in memory
* Balances only need to be tracked since the application is started
* **Python** is the preferred language (Rust or Java submissions accepted as well)

## Transfer API
Build and API that contains the following endpoints: 

|Endpoint   |  Medhod  | Description|
|---|---|---|
|  /transfers | GET  | List tokens and amount transferred |
| /transfers/:rri_id  |  GET | Returns amounts transferred to token with ID rri_id |
| /transfers/:address  |  GET | Returns transfers to the monitored addresses |
| /monitor  |  POST | Adds a list of addresses to be monitored (See example payload below) |
| /monitor  |  DELETE | Deletes all addresses to be monitored |


### Payload to add a list of addresses to monitor
```
{
“Address”: [“rdx1qspd0ge3xj4pqk4dmugw77l7wxfwuepj6fvwpfcvfd89jzwc40add2qxrsud4”]
}
```


# Questions about the Radix network
During the interview we will ask the following questions, so prepare to answer them as you wish.

* What is radix transaction model? Pick any other Layer 1 protocol and compare them.
* Describe how fees work in Radix.
* What is the consensus algorithm used by Radix? Chose any other blockchain/DLT and explain how it compares.

