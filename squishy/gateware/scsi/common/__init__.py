# SPDX-License-Identifier: BSD-3-Clause

__all__ = (
)


"""

+-------------+-------+-------+-------+
|     Name    | SCSI1 | SCSI2 | SCSI3 |
+-------------+-------+-------+-------+
| Arbitration | 2.2us | 2.4us | -     |
+-------------+-------+-------+-------+
| Assertion   | 90ns  | -     | xxxxx |
+-------------+-------+-------+-------+
| Bus Clear   | 800ns | -     | -     |
+-------------+-------+-------+-------+
| Bus Free    | 800ns | -     | -     |
+-------------+-------+-------+-------+
| Bus Set     | 1.8us | -     | 1.6us |
+-------------+-------+-------+-------+
| Bus Settle  | 400ns | -     | -     |
+-------------+-------+-------+-------+
| Cbl Skew    | 10ns  | -     | 4ns   |
+-------------+-------+-------+-------+
| Data Rel    | 400ns | -     | -     |
+-------------+-------+-------+-------+
| Deskew      | 45ns  | -     | -     |
+-------------+-------+-------+-------+
| Hold Time   | 45ns  | -     | xxxxx |
+-------------+-------+-------+-------+
| Negation    | 90ns  | -     | xxxxx |
+-------------+-------+-------+-------+
| Reset Hold  | 25us  | -     | -     |
+-------------+-------+-------+-------+
| Sel Abort   | 200us | -     | -     |
+-------------+-------+-------+-------+
| Sel Timeout | 250ms | -     | -     |
+-------------+-------+-------+-------+
| Disconnect  | xxxxx | 200us | xxxxx |
+-------------+-------+-------+-------+
| Pwr -> sel  | xxxxx | 10s   | -     |
+-------------+-------+-------+-------+
| Rst -> sel  | xxxxx | 250ms | -     |
+-------------+-------+-------+-------+
| Fast Assert | xxxxx | 30ns  | xxxxx |
+-------------+-------+-------+-------+
| Fast Cbl sk | xxxxx | 5ns   | xxxxx |
+-------------+-------+-------+-------+
| Fast Deskew | xxxxx | 20ns  | xxxxx |
+-------------+-------+-------+-------+
| Fast Hold   | xxxxx | 10ns  | xxxxx |
+-------------+-------+-------+-------+
| Fast Neg    | xxxxx | 30ns  | xxxxx |
+-------------+-------+-------+-------+


"""