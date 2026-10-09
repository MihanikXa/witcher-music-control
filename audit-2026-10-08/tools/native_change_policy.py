"""Reviewed normalized text pairs; retain indices identify only authored mod blocks.

All other change blocks are native. New source/baseline text requires re-review.
See review.md for the 21 original skipped hunks.
"""
POLICY = {'r4Game.ws': {'source_sha256': '8cdbac20bd4c2be47b28eff185bf92667794a1c75e1ae961e0c4bf4cda253c66',
               'vanilla_sha256': 'cc54675d7f1000eebeac997a9806c362b07e2d8bc39f2406d7a7d308d6f13ea4',
               'retain_opcodes': [3]},
 'inventoryComponent.ws': {'source_sha256': 'cb22860081e202ccaa104582fa4d08d6570248177d312f56ebb8cb21254fabbf',
                           'vanilla_sha256': '58bf3534268cf73119fac1a239621fe2e6f2a56c987645aa01807f7a6a6bcf96',
                           'retain_opcodes': [11, 13]},
 'ingameMenu.ws': {'source_sha256': 'e6f2e1f5891dc2b3d8189652c93e746e07b6ec8c14ec21f215a202af43e4b678',
                   'vanilla_sha256': 'ebdcdaaddc4ef33b812840523e5480e376e09ce690e3bc2f49327b1d7a5b8b06',
                   'retain_opcodes': [3, 5, 7, 43, 45, 47]},
 'mapMenu.ws': {'source_sha256': 'e7885240afb1d85a2e5dd8f5470eb0ac904ad70cbf4d95ef418ef7ef4863ff62',
                'vanilla_sha256': '5c9634a11eacc38f08712033d68fb3f79907357d5ffc786329d9eaeec8a29042',
                'retain_opcodes': [1, 3, 5, 7, 13]},
 'hudModuleRadialMenu.ws': {'source_sha256': 'c60d2decc0f571b5e6a4f6e1d84434872121c5cd10e6b7757874be40de4bab78',
                            'vanilla_sha256': '139ad6f7f00de20148a059b9b73515f4b1e3dc7a6780f80d7e6523dd9aa49af3',
                            'retain_opcodes': [3, 5, 7, 9, 11, 13]},
 'commonMenu.ws': {'source_sha256': 'e946f2d6ca3763878249989d0b5b3c5615cfa50b5c8fbb1d2b72414abf4c468b',
                   'vanilla_sha256': '6199c7c9c1d190d0312daf9beafbd46f785f3b973314aad57ce83b8bf8e352be',
                   'retain_opcodes': [5, 7]}}
