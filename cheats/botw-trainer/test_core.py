import unittest
from core import plan,CASES
class Tests(unittest.TestCase):
 def test_rupees_chain(self):
  mem={0x100000+0x2cc5fe0:0x2000,0x2000+0xe40:0x3000,0x3000+0x5b08:0x4000}
  self.assertEqual(plan('rupees',0x100000,lambda a:mem[a]),[(0x4000+0x5d90,(999999).to_bytes(4,'little'))])
 def test_null_rejected(self):
  with self.assertRaises(ValueError):plan('weapon_dur',0,lambda a:0)
 def test_unknown_rejected(self):
  with self.assertRaises(ValueError):plan('bad',0,lambda a:0x1000)
 def test_bow_modes_conflict_group(self):
  for k in ['bow_attack','bow_fast_attack','bow_fast','bow_five']:self.assertEqual(CASES[k]['group'],'bow_effect')
 def test_width(self):
  self.assertEqual(len(plan('health',0,lambda a:0x1000)[0][1]),1)
  self.assertEqual(len(plan('arrows',0,lambda a:0x1000)[0][1]),2)
 def test_no_material_replacement(self):
  self.assertNotIn('fairy',CASES)
if __name__=='__main__':unittest.main()

class RecoveryTests(unittest.TestCase):
 def test_empty_restore_is_not_success(self):
  from core import require_restore_records
  with self.assertRaises(ValueError):require_restore_records({})
 def test_failed_backup_not_committed(self):
  from core import atomic_backup
  from unittest.mock import patch
  from pathlib import Path
  import tempfile
  with tempfile.TemporaryDirectory() as t:
   src=Path(t)/'src';src.mkdir();(src/'save').write_text('original');dst=Path(t)/'backup'
   def broken(s,d):
    Path(d).mkdir();raise OSError('interrupted')
   with patch('shutil.copytree',side_effect=broken):
    with self.assertRaises(OSError):atomic_backup(src,dst)
   self.assertFalse(dst.exists())
   atomic_backup(src,dst);self.assertEqual((dst/'save').read_text(),'original')

class MaterialsTests(unittest.TestCase):
 def test_only_existing_materials(self):
  from core import material_entries
  import struct
  base=0x1000;data=bytearray(0x298*4)
  for i,kind,qty in [(0,7,230),(1,9,1),(2,8,5),(3,7,0)]:
   off=i*0x298;struct.pack_into('<i',data,off+0x18,kind);struct.pack_into('<i',data,off+0x20,qty);data[off+0x25]=1
   struct.pack_into('<Q',data,off+0x30,base+off+0x3c);data[off+0x3c:off+0x3c+13]=b'Item_Fruit_A\0'
  self.assertEqual(material_entries(bytes(data),base),[(base,'Item_Fruit_A',230)])
 def test_wrong_string_pointer_rejected(self):
  from core import material_entries
  import struct
  d=bytearray(0x298);struct.pack_into('<i',d,0x18,7);struct.pack_into('<i',d,0x20,5);d[0x25]=1
  self.assertEqual(material_entries(bytes(d),0x1000),[])

class ArrowJournalTests(unittest.TestCase):
 def test_switch_arrow_keeps_separate_backups(self):
  from core import record_key,migrate_arrow_records
  records={'arrows':{'code':'arrows','identity':b'IceArrow'.hex(),'values':[{'address':123,'before':'ac00','after':'e703'}]}}
  migrate_arrow_records(records)
  self.assertIn(record_key('arrows',b'IceArrow'.hex()),records)
  self.assertNotIn(record_key('arrows',b'BombArrow_A'.hex()),records)
  self.assertEqual(next(iter(records.values()))['values'][0]['before'],'ac00')
 def test_arrow_lookup_ignores_current_selection_and_invalid_slots(self):
  from core import arrow_entries
  import struct
  base=0x1000;data=bytearray(0x298*3)
  for i,name,kind in [(0,b'IceArrow',2),(1,b'BombArrow_A',2),(2,b'Weapon_Bow_001',1)]:
   o=i*0x298;struct.pack_into('<i',data,o+0x18,kind);struct.pack_into('<i',data,o+0x20,207);data[o+0x25]=1
   struct.pack_into('<Q',data,o+0x30,base+o+0x3c);data[o+0x3c:o+0x3c+len(name)+1]=name+b'\0'
  self.assertEqual(arrow_entries(data,base),[(base,'IceArrow',207),(base+0x298,'BombArrow_A',207)])
 def test_other_groups_unchanged(self):
  from core import record_key
  self.assertEqual(record_key('bow_fast','a'),'bow_effect')
