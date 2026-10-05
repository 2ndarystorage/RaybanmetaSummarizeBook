import Foundation
import Security

enum KeychainStore {
  private static var query: [String: Any] {
    [kSecClass as String: kSecClassGenericPassword,
     kSecAttrService as String: "MetaBookReader",
     kSecAttrAccount as String: "openai-api-key"]
  }

  static func read() -> String {
    var request = query
    request[kSecReturnData as String] = true
    request[kSecMatchLimit as String] = kSecMatchLimitOne
    var result: CFTypeRef?
    guard SecItemCopyMatching(request as CFDictionary, &result) == errSecSuccess,
          let data = result as? Data else { return "" }
    return String(data: data, encoding: .utf8) ?? ""
  }

  static func save(_ value: String) throws {
    let data = Data(value.trimmingCharacters(in: .whitespacesAndNewlines).utf8)
    if data.isEmpty {
      let status = SecItemDelete(query as CFDictionary)
      guard status == errSecSuccess || status == errSecItemNotFound else { throw Failure(status: status) }
      return
    }
    let status = SecItemUpdate(query as CFDictionary, [kSecValueData as String: data] as CFDictionary)
    if status == errSecItemNotFound {
      var item = query
      item[kSecValueData as String] = data
      item[kSecAttrAccessible as String] = kSecAttrAccessibleWhenUnlockedThisDeviceOnly
      let added = SecItemAdd(item as CFDictionary, nil)
      guard added == errSecSuccess else { throw Failure(status: added) }
    } else if status != errSecSuccess {
      throw Failure(status: status)
    }
  }

  struct Failure: LocalizedError {
    let status: OSStatus
    var errorDescription: String? { "APIキーを保存できませんでした（\(status)）。" }
  }
}
