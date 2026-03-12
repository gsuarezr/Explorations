// SPDX-License-Identifier: MIT

// Fund part

//Withdraw part

pragma solidity ^0.8.18;
import {Script, console} from "forge-std/Script.sol";
import {DevOpsTools} from "foundry-devops/src/DevOpsTools.sol";
import {FundMe} from "../src/FundMe.sol";

contract FundFundMe is Script {
    uint256 constant SEND_VALUE = 0.01 ether;

    function fundFundMe(address deployed) public {
        vm.startBroadcast();
        FundMe(payable(deployed)).fund{value: SEND_VALUE}();
        vm.stopBroadcast();
        console.log("Sent %s to the deployed contract", SEND_VALUE);
    }

    function run() external {
        address deployed = DevOpsTools.get_most_recent_deployment(
            "FundMe",
            block.chainid
        );
        vm.startBroadcast();
        fundFundMe(deployed);
        vm.stopBroadcast();
    }
}

contract WithdrawFundMe is Script {
    function withdrawFundMe(address deployed) public {
        vm.startBroadcast();
        FundMe(payable(deployed)).withdraw();
        vm.stopBroadcast();
        console.log("Withdrew contract balance");
    }

    function run() external {
        address deployed = DevOpsTools.get_most_recent_deployment(
            "FundMe",
            block.chainid
        );
        vm.startBroadcast();
        withdrawFundMe(deployed);
        vm.stopBroadcast();
    }
}
