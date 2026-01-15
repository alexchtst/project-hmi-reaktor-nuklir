# pdfl `digsilent_pf_lib`

> Dokumentasi singkat dan contoh penggunaan modul `digsilent_pf_lib.py` untuk berinteraksi dengan PowerFactory (DIgSILENT PowerFactory) dari Python.

> Dokumentasi dan output lengkap tersedia di example.ipynb pada https://github.com/alexchtst/project-hmi-reaktor-nuklir/blob/main/library/example.ipynb

---

## Deskripsi

`digsilent_pf_lib.py` menyediakan kelas `DigsilentPowerFactoryLibrary` yang membungkus (wrapper) operasi umum untuk:

* Menghubungkan ke aplikasi PowerFactory,
* Mengaktifkan project PowerFactory,
* Mendeteksi study case dan event,
* Menjalankan loadflow (steady-state) dan mengumpulkan hasil,
* Menjalankan simulasi dinamik (time-domain), mengatur event, dan mengekspor hasil.

---

## Prasyarat

1. **DIgSILENT PowerFactory** terinstall pada mesin (biasanya Windows).
2. Akses ke modul Python `powerfactory` yang disediakan oleh instalasi PowerFactory (biasanya path ke direktori instalasi harus ditambahkan ke `sys.path` — modul ini melakukan `sys.path.append(digsilent_path)`).
3. Python (3.8+) yang mampu mengeksekusi skrip yang memanggil COM API PowerFactory.
4. Menjalankan notebook / skrip pada mesin yang sama dengan PowerFactory (atau environment yang punya akses library `powerfactory`).

> Catatan: jika path ke instalasi PowerFactory tidak ditemukan, konstruktor akan mencetak peringatan. Pastikan `digsilent_path` merujuk ke folder yang benar.

---

## Instalasi sederhana

Letakkan `digsilent_pf_lib.py` di folder kerja Anda (provinsi sudah diupload: ). Tidak perlu packaging khusus; import langsung dari notebook / script:

```python
from dspfl.digsilent_pf_lib import DigsilentPowerFactoryLibrary
```

---

## Inisialisasi / Konstruktor

```python
DigsilentPowerFactoryLibrary(digsilent_path, proj_name=None, case_name=None)
```

* `digsilent_path` (str): path folder instalasi PowerFactory (harus berisi modul `powerfactory`).
* `proj_name` (str, optional): nama project yang ingin diaktifkan saat inisialisasi.
* `case_name` (str, optional): nama study case default.

Setelah inisialisasi, objek memiliki properti seperti `pf_app`, `project_app`, `cases_app`, dan flag `__ready_to_run__`.

Contoh:

```python
lib = DigsilentPowerFactoryLibrary(r"C:\Program Files\DIgSILENT\PowerFactory 2023", proj_name="MyProject")
```

---

## API utama (method)

### `detect_project_names()`

Mendeteksi semua project yang dapat diakses oleh current user.

* Return: `(bool, message, list_of_project_names)`.

Contoh:

```python
ok, msg, projects = lib.detect_project_names()
```

---

### `detect_study_cases()`

Mengambil semua study case di project aktif.

* Return: `(bool, message, list_of_case_names)`.

Contoh:

```python
ok, msg, cases = lib.detect_study_cases()
```

---

### `detect_event_in_case(case_specific_name=None)`

Mengambil daftar event dari study case tertentu (atau `self.case_name` jika parameter None).

* Return: `(bool, message, list_of_event_dicts)`
* `event_dict` minimal berisi: `name`, `class`, dan jika tersedia `target`, `time`, `switch_state`.

Contoh:

```python
ok, msg, events = lib.detect_event_in_case("LoadFlow_Case1")
```

---

### `connect_digsilent_pf_project(connect_to_project=None)`

Mengganti (activate) project PowerFactory.

* Return: `(bool, message)`.

Contoh:

```python
ok, msg = lib.connect_digsilent_pf_project("AnotherProject")
```

---

### `running_loadflow(case_specific_name=None)`

Menjalankan powerflow (loadflow) pada study case yang dipilih, lalu mengumpulkan hasil (buses, generators, lines, loads, transformers).

* Return: `(bool, message, result_dict)`
* `result_dict` berisi keys: `project`, `study_case`, dan list data untuk tiap tipe objek.

Contoh:

```python
ok, msg, data = lib.running_loadflow("Case_LF_1")
if ok:
    print(data["buses"][:3])
```

---

### `running_dynamic(...)`

Menjalankan simulasi dinamik dengan opsi pengaturan:

* `case_specific_name`, `start_calc`, `start_time_simulation`, `stop_time_simulation`, `step_size`,
* `events_config` (dictionary untuk konfigurasi event — nama event, apakah aktif, config khusus untuk short-circuit, switch, dsb),
* `properties_data_name` (mapping tipe elemen ke variabel yang ingin dimonitor).

Return: `(bool, message, result_data)`
`result_data` berisi header kolom, data baris time-series, jumlah baris/kolom, rentang waktu, dsb.

Contoh minimal:

```python
ok, msg, dyn = lib.running_dynamic(
    case_specific_name="DynCase1",
    start_time_simulation=0,
    stop_time_simulation=2.0,
    step_size=0.01,
    properties_data_name={"ElmSym": ["m:P:bus1", "m:Q:bus1"], "ElmTerm": ["m:fehz"]}
)
if ok:
    header = dyn["header"]
    rows = dyn["data"]
```

Contoh pembuatan konfigurasi event (fault + clear):

```python
events_cfg = {
    "Fault1": {
        "event_data": {"name": "FaultAtBusX", "target": "Bus X", "class": "EvtShc"},
        "in_service": True,
        "configured": True,
        "config": {"start_fault": 0.1, "clear_fault": 0.2, "fault_type": 1}
    }
}
ok, msg, dyn = lib.running_dynamic(case_specific_name="DynCase1", events_config=events_cfg)
```

---

### `safe_getattr(obj, attr, default=0)`

Utility untuk safe-get attribute dari objek PowerFactory. Mengembalikan `default` jika tidak tersedia.

---

## Penanganan error & logging

* Method mengembalikan tuple `(bool, message, data)` — periksa nilai boolean sebelum memakai `data`.
* Jika terjadi exception, library berusaha menangkap dan mengembalikan pesan error yang cukup informatif; untuk simulasi dinamik juga mengikutsertakan stacktrace dalam pesan error.
* Library mencetak progress & info ke output saat berjalan (contoh: `[INFO]: Collecting bus loadflow data...`).

---

## Contoh penggunaan cepat (snippet)

```python
from digsilent_pf_lib import DigsilentPowerFactoryLibrary

# inisialisasi
lib = DigsilentPowerFactoryLibrary(r"C:\Program Files\DIgSILENT\PowerFactory 2023", proj_name="MyProject", case_name="Case1")

# cek project
ok, msg, projects = lib.detect_project_names()

# mendapat study cases
ok, msg, cases = lib.detect_study_cases()

# jalankan loadflow
ok, msg, loadflow_result = lib.running_loadflow()

# jalankan dynamic dengan monitoring variabel dasar
ok, msg, dyn_result = lib.running_dynamic(
    start_time_simulation=0,
    stop_time_simulation=1.0,
    step_size=0.01,
    properties_data_name={"ElmSym": ["m:P:bus1", "m:Q:bus1"], "ElmTerm": ["m:fehz"]}
)
```

---

## Notebook contoh

File `example.ipynb` yang Anda upload berisi contoh pemakaian modul ini (inisialisasi, pemanggilan method, dan contoh mengekspor/menampilkan output). Jalankan notebook pada mesin yang sama dengan PowerFactory agar `powerfactory` module dapat ter-load. (Notebook ada di workspace Anda.)

---

## Batasan & catatan praktis

* Library mengandalkan API `powerfactory` yang hanya tersedia dari instalasi PowerFactory; tidak dapat dijalankan di mesin tanpa instalasi tersebut.
* Uji di environment Windows yang sama dengan PowerFactory (PowerFactory biasanya bereaksi berbeda jika dijalankan sebagai service / user berbeda).
* Pastikan project `.pfd` dan study case sudah ter-load di PowerFactory GUI bila diperlukan.
* Perhatikan permission dan konfigurasi PowerFactory untuk scripting (beberapa instalasi membatasi akses API).