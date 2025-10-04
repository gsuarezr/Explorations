//SPDX-License-Identifier: MIT

pragma solidity ^0.8.18;
import {Script} from "forge-std/Script.sol";
import {FundMe} from "../src/FundMe.sol";
import {HelperConfig} from "./HelperConfig.s.sol";
import {Test, console} from "forge-std/Test.sol";

contract DeployFundMe is Script {
    function run() external returns (FundMe) {
        // Before vm so gas does not get spent
        HelperConfig helperConfig = new HelperConfig();
        address priceFeed = helperConfig.activeChain();
        console.log(priceFeed);
        vm.startBroadcast();
        FundMe fundMe = new FundMe(priceFeed);
        vm.stopBroadcast();
        return fundMe;
    }
}
