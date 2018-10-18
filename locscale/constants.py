
# **************************************************************************
# *
# * Authors:    Yunior C. Fonseca Reyna (cfonseca@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************
import os


# we declarate global constants to multiple usage
LOCSCALE_HOME_VAR = 'LOCSCALE_HOME'
EMAN2DIR_VAR = 'EMAN2DIR'
LOCSCALE_HOME = os.environ.get(LOCSCALE_HOME_VAR, '')
EMAN2DIR = os.environ.get(EMAN2DIR_VAR, '')

# Supported versions
V0_1 = '0.1'

# Emman Supported versions
V2_11 = '2.11'
V2_12 = '2.12'
V2_21 = '2.21'

