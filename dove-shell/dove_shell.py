import mpi4py.MPI as MPI
import subprocess
import click
import json
import os

from security import import_key, encode_encrypt, decrypt_decode
from datetime import datetime


@click.command()
@click.option('--config_file', type=str, help='Filepath to where configs are saved')
def dove_shell(config_file: str):
    """Setup a connection between two proccesses/two cores/two nodes/two clusters

    Parameters:

        \b
        config_file: str << Filepath to where configs are saved

    Returns:

        \b
        None
    """
    with open(config_file) as f:
        config = json.load(f)
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        # client-like side

        # setup keys
        client_private_key = config['client_private_key']
        server_public_key = config['server_public_key']
        client_private_key, server_public_key = import_key(client_private_key, server_public_key)

        # enter client-server-like loop
        while True:
            cwd = decrypt_decode(comm.recv(source=1, tag=42), client_private_key)

            cmd = input(f'{cwd}#>')

            # break client-sever like loop
            # if cmd.lower() == 'dovestop':
            #     comm.send(encode_encrypt(cmd, server_public_key), dest=1, tag=41)
            #     break

            comm.send(encode_encrypt(cmd, server_public_key), dest=1, tag=42)

            output = decrypt_decode(comm.recv(source=1, tag=42), client_private_key)
            print(output)
        # end of client-like side
    elif rank == 1:
        # server-like side

        # setup keys
        server_private_key = config['server_private_key']
        client_public_key = config['client_public_key']
        server_private_key, client_public_key = import_key(server_private_key, client_public_key)
        
        # enter server-client-like loop
        while True:
            cwd = os.getcwd()
            comm.send(encode_encrypt(cwd, client_public_key), dest=0, tag=42)

            cmd = decrypt_decode(comm.recv(source=0, tag=42), server_private_key)

            # break server-client-like loop
            # if cmd.lower() == 'dovestop':
            #     break
            
            # save command history
            time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(config['log_file'], 'a+') as f:
                f.write(f'[On] {time_now} [in] {cwd} [executed] {cmd}\n')

            output = subprocess.getoutput(cmd)
            comm.send(encode_encrypt(output, client_public_key), dest=0, tag=42)
        # end of server-like side


if __name__ == '__main__':
    dove_shell()
    