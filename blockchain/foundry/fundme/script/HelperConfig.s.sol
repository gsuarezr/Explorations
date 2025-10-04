//SPDX-License-Identifier: MIT

// Keep track of contract address across different chains

pragma solidity ^0.8.18;
import {Script} from "forge-std/Script.sol";
import {MockV3Aggregator} from "../test/mocks/MockV3Aggregator.sol";

contract HelperConfig is Script {
    // Deploy Mock price feed when using Anvil local chain
    struct ChainConfig {
        address priceFeed; //ETH/USD Oracle Feed
    }
    // Select Active Network
    ChainConfig public activeChain;
    uint8 public constant DECIMALS = 8;
    int256 public constant INITIAL_PRICE = 2000e8;
    uint256 public constant SEPOLIA_ID = 11155111;

    constructor() {
        // Check if the ChainID corresponds to Sepolia
        if (block.chainid == SEPOLIA_ID) {
            activeChain = getSepoliaConfig();
        } else {
            // if not in Sepolia we are in Anvil
            activeChain = getAnvilConfig();
        }
    }

    function getSepoliaConfig() public pure returns (ChainConfig memory) {
        ChainConfig memory sepoliaConfig = ChainConfig({
            priceFeed: 0x694AA1769357215DE4FAC081bf1f309aDC325306
        });
        return sepoliaConfig;
    }

    function getAnvilConfig() public returns (ChainConfig memory) {
        // Check is we have created an anvill config
        if (activeChain.priceFeed != address(0)) {
            return activeChain;
        }

        // Deply dummy contract
        vm.startBroadcast();
        MockV3Aggregator mockFeed = new MockV3Aggregator(
            DECIMALS,
            INITIAL_PRICE
        );
        vm.stopBroadcast();
        ChainConfig memory anvilConfig = ChainConfig(address(mockFeed));
        return anvilConfig;
    }
}
