import click

from Crypto.PublicKey import RSA
from pathlib import Path


@click.command()
@click.option('--save_dir', default='.', help='Directory ')
def gen_pair(save_dir: str='.'):
    """Generate public and private key then save to files

        \b
        private key is saved to `private.dove.txt`
        public key is saved to `public.dove.txt`
    
    Parameters:
        
        \b
        save_dir: str << Directory to save both keys
    
    Returns:
        
        \b
        None
    """

    key = RSA.generate(2048)
    Path(save_dir).mkdir(exist_ok=True)
    private = key.export_key()
    private_path = Path(save_dir).joinpath('private.dove.txt')
    with open(private_path, 'wb') as f:
        f.write(private)

    # Generate public key from a RSA key
    public = key.publickey().export_key()
    public_path = Path(save_dir).joinpath('public.dove.txt')
    with open(public_path, 'wb') as f:
        f.write(public)

    
if __name__ == '__main__':
    gen_pair()