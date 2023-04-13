import subprocess

from algosdk import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from examples.application.asset import approval_program, clear_state_program
from pyteal import *

from secrets import account_mnemonics
from election_params import local_ints, local_bytes, global_ints, \
    global_bytes, relative_election_end, num_vote_options, vote_options
from helper import compile_program, wait_for_confirmation, int_to_bytes, read_global_state, read_local_state
from secrets import account_mnemonics, algod_token, algod_address, algod_headers
from election_params import vote_options, num_vote_options


# Define keys, addresses, and token
account_private_keys = [mnemonic.to_private_key(mn) for mn in account_mnemonics]
account_addresses = [account.address_from_private_key(sk) for sk in account_private_keys]

# Declare application state storage for local and global schema
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema, app_args):
    """
    Create a new application from the compiled approval_program, clear_program
    using the application arguments app_args
    Return the newly created application ID
    """
    # TODO: define sender as creator
    sender = account.address_from_private_key(private_key)
    # TODO: declare the on_complete transaction as a NoOp transaction
    on_complete = transaction.OnComplete.NoOpOC.real
    # TODO: get node suggested parameters
    params = client.suggested_params()
    # TODO: create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, approval_program, clear_program, global_schema, local_schema, app_args)
    # TODO: sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    # TODO: send transaction
    client.send_transactions([signed_txn])
    # TODO: await confirmation
    wait_for_confirmation(client, tx_id)
    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id


def create_vote_app(client, creator_private_key, election_end, num_vote_options, vote_options):
    """
    Create/Deploy the voting app
    This function uses create_app and return the newly created application ID
    """
    # TODO:
    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(
        approval_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    approval_program_compiled = compile_program(client, approval_program_teal)
    # Do the same for PyTeal clear state program
    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(
        clear_state_program_ast, mode=Mode.Application, version=5
    )
    # compile program to binary
    clear_state_program_compiled = compile_program(
        client, clear_state_program_teal
    )

    # create list of bytes for application arguments
    application_args = [election_end, num_vote_options, vote_options]
    # TODO: Create new application
    app_id = create_app(
        client,
        creator_private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
        application_args,
    )

    return app_id



def main():
    # TODO: Initialize algod client and define absolute election end time fom the status of the last round.
    # TODO: Deploy the app and print the global state.
    # Initialize the Algod client
    algod_client = algod.AlgodClient(algod_token, algod_address, algod_headers)

    # Get the last round information
    last_round = algod_client.status()["lastRound"]

    # Define the absolute election end time
    election_end = last_round + relative_election_end

    # Deploy the app
    app_id = create_vote_app(algod_client, account_private_keys[0], election_end, num_vote_options, vote_options)
    print("App ID:", app_id)

    # Print the global state
    app_info = read_global_state(algod_client, app_id)
    print("Global state:", app_info)


if __name__ == "__main__":
    main()
