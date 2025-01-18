# -*- coding: utf-8 -*-

import numpy as np

d360 = np.arange(361 )

bucket = (d360 + 45/2) // 45 % 8
