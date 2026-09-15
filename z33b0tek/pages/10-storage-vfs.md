# Storage and the VFS Namespace

Titles never see host paths. Every file access goes through the VFS, which
presents a flat namespace built from the firmware partitions plus per-application
directories.

## Path space

| Prefix | Meaning |
|---|---|
| fs:/mod/<appid>/ | the application's own module directory |
| fs:/~0x<clsid>/ | the application's private directory |
| fs:/mif/ | module information files, named by app ID |
| fs:/shared/ | files shared between applications |
| fs:/fs/ | the raw filesystem view used by system components |

Observed naming rules:

- Module directories use the decimal app ID, for example fs:/mod/274755/.
- Private directories use a tilde followed by the class ID in hex.
- Metadata files are named by app ID, for example fs:/mif/274755.mif.

## Interfaces

<!-- BEGIN GENERATED: IFileMgr -->
_Generated from the public SDK header `AEEIFileMgr.h`. Inheritance chain: IBase, IFileMgr._

Base slots: **IBase → IFileMgr**, so slot 0 is the first method of IBase and the first method of IFileMgr starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | OpenFile | IFile * | this, const char *pszFile, OpenFileMode mode |
| 3 | GetInfo | int | this, const char *pszName, FileInfo * pInfo |
| 4 | Remove | int | this, const char *pszName |
| 5 | MkDir | int | this, const char *pszDir |
| 6 | RmDir | int | this, const char *pszDir |
| 7 | Test | int | this, const char *pszName |
| 8 | GetFreeSpace | uint32 | this, uint32 * pdwTotal |
| 9 | GetLastError | int | this |
| 10 | EnumInit | int | this, const char *pszDir, boolean bDirs |
| 11 | EnumNext | boolean | this, FileInfo * pInfo |
| 12 | Rename | int | this, const char * pszSrc, const char * pszDest |
| 13 | EnumNextEx | boolean | this, AEEFileInfoEx * pInfo |
| 14 | SetDescription | int | this, const char * pszName,AECHAR * pszDesc |
| 15 | GetInfoEx | int | this, const char * pszName,AEEFileInfoEx * pi |
| 16 | Use | int | this, const char * pszName,boolean bUse |
| 17 | GetFileUseInfo | int | this, AEEFileUseInfo *pfu |
| 18 | ResolvePath | int | this, const char *cpszIn, char *pszOut, int *pnOutLen |
| 19 | CheckPathAccess | int | this, const char *cpszIn, uint32 dwDesiredRights, uint32 *pdwActualRights |
| 20 | GetFreeSpaceEx | int | this, const char *cpszPath, uint32 * pdwTotal, uint32 *pdwFree |
<!-- END GENERATED: IFileMgr -->

<!-- BEGIN GENERATED: IFile -->
_Generated from the public SDK header `AEEIFile.h`. Inheritance chain: IBase, IAStream, IFile._

Base slots: **IBase → IFile**, so slot 0 is the first method of IBase and the first method of IFile starts at the first free index.

| Slot | Method | Returns | Arguments |
|---|---|---|---|
| 0 | AddRef | uint32 | this |
| 1 | Release | uint32 | this |
| 2 | Readable | void | this, void (*pfnNotify)(void*), void * pUser |
| 3 | Read | int32 | this, void * pDest, uint32 nWant |
| 4 | Cancel | void | this, void (*pfnNotify)(void*), void * pUser |
| 5 | Write | uint32 | this, PACKED const void * pBuffer, uint32 dwCount |
| 6 | GetInfo | int | this, FileInfo * pInfo |
| 7 | Seek | int32 | this, FileSeekType seek, int32 position |
| 8 | Truncate | int | this, uint32 truncate_pos |
| 9 | GetInfoEx | int | this, AEEFileInfoEx * pi |
| 10 | SetCacheSize | int32 | this, int nSize |
| 11 | Map | void * | this, void * pStart, uint32 dwSize, int protections,int flags, uint32 dwOffset |
<!-- END GENERATED: IFile -->

## Path rules that trip implementations

| Rule | Detail |
|---|---|
| Case | the namespace is case sensitive in practice; titles use the exact case they shipped with |
| Leading slash | paths are given with the fs:/ prefix, without a leading slash |
| Directories | enumeration returns entries, not full paths; the caller joins them |
| Writable areas | only the application's private directory is writable |
| Free space | GetFreeSpace is called by titles before saving; returning zero blocks progress |

## Firmware-level storage

Below the VFS, the device uses EFS2, a Qualcomm filesystem layered on NAND.
Firmware boot requires a NAND controller model and the EFS2 structures. Running
a title does not: a title only needs the VFS view of the files its archives and
its private directory contain.

| Layer | Needed to boot firmware | Needed to run a title |
|---|---|---|
| NAND controller | yes | no |
| EFS2 structures | yes | no |
| VFS namespace | no | yes |
| Archive mounting (GGZ, BAR) | no | yes |
| Module information (MIF) | no | yes for the shell UI |

Keeping that boundary explicit prevents the most expensive kind of scope creep:
building a full storage stack for titles that only need a directory tree.

## Journal and recovery

The firmware keeps a journal for crash recovery. A loader that mounts a
filesystem image should tolerate a journal that was not cleanly closed, because
dumps taken from a live device rarely are.

Evidence: path rules and interface layouts from the SDK headers and from the
firmware filesystem image. Layer boundary from the observed behaviour of titles
that never touch the raw filesystem.
