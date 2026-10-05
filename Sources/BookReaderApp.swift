import MWDATCore
import SwiftUI

@main
struct BookReaderApp: App {
  private let setupError: String?

  init() {
    do {
      try Wearables.configure()
      setupError = nil
    } catch {
      setupError = error.localizedDescription
    }
  }

  var body: some Scene {
    WindowGroup {
      if let setupError {
        ContentUnavailableView("初期設定に失敗しました", systemImage: "exclamationmark.triangle", description: Text(setupError))
      } else {
        BookReaderView()
      }
    }
  }
}
